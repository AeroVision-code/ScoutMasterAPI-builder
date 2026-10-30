"""Generate client methods for API endpoints the client doesn't cover yet.

Downloads the ScoutMaster OpenAPI spec, finds the operations no hand-written
method reaches (the same check as tests/test_spec_coverage.py) and writes a
method for each of them to scoutmasterapi_builder/generated.py.

ScoutMasterAPI includes that class last, so hand-written methods always win.
To improve a generated method, write a proper one in the right module and run
this script again: the generated one is then dropped. The file is rewritten
from scratch on every run, so never edit it by hand.

Usage, from the repo root (with the package installed: pip install -e ".[dev]"):

    python scripts/generate_endpoints.py               # production spec
    python scripts/generate_endpoints.py --dev         # dev spec
    python scripts/generate_endpoints.py --spec FILE_OR_URL
    python scripts/generate_endpoints.py --check       # only report; exit 1 if out of date
"""
import argparse
import keyword
import re
import sys
import textwrap
from collections import namedtuple
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUTPUT = REPO / "scoutmasterapi_builder" / "generated.py"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import spec_coverage as sc  # noqa: E402

TYPES = {"string": "str", "integer": "int", "number": "float", "boolean": "bool",
         "array": "list", "object": "dict"}
CONCEPTUAL_NOTE = "⚠️ Conceptual"
WIDTH = 88

# One method argument. `key` is the API's name (path/query parameter or body field).
Arg = namedtuple("Arg", "name key where required type description")

EMPTY_MODULE = '''"""API endpoints generated from the ScoutMaster OpenAPI spec (none yet)."""


class GeneratedEndpoints:
    """No endpoints are missing from the hand-written client."""
'''


# --- names and types -----------------------------------------------------------

def snake(name):
    """camelCase / PascalCase / kebab-case -> a valid snake_case Python name."""
    s = re.sub(r"[^0-9a-zA-Z]+", "_", name)
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", s)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", s)
    s = s.strip("_").lower() or "value"
    if s[0].isdigit():
        s = "_" + s
    if keyword.iskeyword(s) or s == "self":
        s += "_"
    return s


def type_of(spec, schema):
    """Python type name for a schema, for docstrings."""
    s = sc.resolve(spec, schema or {})
    t = s.get("type")
    if isinstance(t, list):
        return " or ".join(TYPES.get(x, x) for x in t if x != "null")
    if t:
        return TYPES.get(t, t)
    for combo in ("anyOf", "oneOf", "allOf"):
        if combo in s:
            names = sorted({type_of(spec, x) for x in s[combo]} - {"null"})
            return " or ".join(names) if combo != "allOf" else (names[0] if names else "dict")
    return "dict" if "properties" in s else "value"


def object_fields(spec, schema):
    """(properties, required names) of an object schema, merging allOf."""
    s = sc.resolve(spec, schema or {})
    props, required = dict(s.get("properties", {})), set(s.get("required", []))
    for part in s.get("allOf", []):
        p, r = object_fields(spec, part)
        props.update(p)
        required |= r
    return props, required


def clean(text):
    """One line of text without the spec's conceptual disclaimer."""
    text = " ".join((text or "").split())
    text = re.sub(r"⚠️\s*Conceptual:?[^.]*\.\s*", "", text)
    text = re.sub(r"^⚠️\s*Conceptual\s*(—|-)?\s*", "", text)
    return text.replace("\\", "\\\\").replace('"""', "'''").strip()


def first_sentence(text):
    text = clean(text)
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    return (m.group(1) if m else text)[:200]


# --- reading one operation -------------------------------------------------------

def collect_args(spec, op):
    """The method arguments for an operation, in signature order."""
    d = op.definition
    params = [sc.resolve(spec, p) for p in d.get("parameters", [])]
    path_params = {p["name"]: p for p in params if p.get("in") == "path"}
    args = []
    for name in re.findall(r"\{([^}]+)\}", op.path):
        p = path_params.get(name, {})
        args.append(Arg(snake(name), name, "path", True, type_of(spec, p.get("schema")),
                        first_sentence(p.get("description")) or f"Path parameter {name}."))
    for p in params:
        if p.get("in") == "query":
            args.append(Arg(snake(p["name"]), p["name"], "query", bool(p.get("required")),
                            type_of(spec, p.get("schema")),
                            first_sentence(p.get("description")) or f"Query parameter {p['name']}."))

    body = sc.resolve(spec, d.get("requestBody") or {})
    content = body.get("content") or {}
    if "multipart/form-data" in content:
        props, required = object_fields(spec, content["multipart/form-data"].get("schema"))
        for key, prop in props.items():
            prop = sc.resolve(spec, prop)
            if prop.get("format") == "binary":
                args.append(Arg("file_path", key, "file", True, "str", "Local path of the file to upload."))
            else:
                args.append(Arg(snake(key), key, "form", key in required, type_of(spec, prop),
                                first_sentence(prop.get("description")) or f"Form field {key}."))
    elif "application/json" in content:
        schema = content["application/json"].get("schema")
        props, required = object_fields(spec, schema)
        if props:
            for key, prop in props.items():
                prop = sc.resolve(spec, prop)
                args.append(Arg(snake(key), key, "body", key in required, type_of(spec, prop),
                                first_sentence(prop.get("description")) or f"Body field {key}."))
        else:
            args.append(Arg("payload", None, "payload", bool(body.get("required")),
                            type_of(spec, schema), "Request body."))

    # Unique Python names: a body field may share a name with a parameter.
    seen, unique = set(), []
    for a in args:
        name = a.name
        while name in seen:
            name = f"{a.where}_{name}"
        seen.add(name)
        unique.append(a._replace(name=name))
    required = [a for a in unique if a.required and a.key != "lang"]
    optional = [a for a in unique if not a.required or a.key == "lang"]
    return required + optional


def returns_table(spec, op):
    """True when the response is a list or GeoJSON, i.e. worth _format_output."""
    for code in ("200", "201"):
        response = sc.resolve(spec, op.definition.get("responses", {}).get(code, {}))
        for content_type, content in (response.get("content") or {}).items():
            if "geo+json" in content_type:
                return True
            schema = sc.resolve(spec, content.get("schema", {}))
            if schema.get("type") == "array":
                return True
            props, _ = object_fields(spec, schema)
            if "data" in props and sc.resolve(spec, props["data"]).get("type") == "array":
                return True
    return False


# --- rendering ---------------------------------------------------------------------

def render_method(spec, op, name):
    args = collect_args(spec, op)
    query = [a for a in args if a.where == "query"]
    body = [a for a in args if a.where in ("body", "payload")]
    form = [a for a in args if a.where == "form"]
    file_arg = next((a for a in args if a.where == "file"), None)
    keys = {a.key for a in query}
    paged = op.method == "GET" and {"page", "limit"} <= keys
    table = op.method == "GET" and returns_table(spec, op)

    out = []
    if op.conceptual:
        out.append("    @conceptual")
    sig = ["self"] + [a.name for a in args if a.required and a.key != "lang"] \
        + [f"{a.name}=None" for a in args if not a.required or a.key == "lang"]
    line = f"    def {name}({', '.join(sig)}):"
    if len(line) <= WIDTH:
        out.append(line)
    else:
        out.append(f"    def {name}(")
        out += [f"        {s}," for s in sig]
        out.append("    ):")

    # Docstring
    d = op.definition
    summary = clean(d.get("summary")) or first_sentence(d.get("description")) or f"{op.method} {op.path}"
    summary = summary[:1].upper() + summary[1:]
    doc = [summary if summary.endswith((".", "!", "?")) else summary + "."]
    description = clean(d.get("description"))
    # Don't repeat the summary when the description starts with it.
    if description.lower().startswith(summary.rstrip(".!?").lower()):
        description = description[len(summary.rstrip(".!?")):].lstrip(".!? ")
    if description:
        doc += [""] + textwrap.wrap(description, WIDTH - 8)
    if op.conceptual:
        doc += ["", f"{CONCEPTUAL_NOTE} endpoint: not yet implemented server-side, may change."]
    doc += ["", f"{op.method} {op.path} ({op.operation_id}), generated from the API spec."]
    if paged:
        doc += ["Without `page` or `limit`, all pages are fetched and combined."]
    if args:
        doc.append("Args:")
        for a in args:
            optional = ", optional" if (not a.required or a.key == "lang") else ""
            text = a.description or ""
            if a.key == "lang":
                if text and not text.endswith((".", "!", "?")):
                    text += "."
                text = (text + " Defaults to the client's lang.").strip()
            doc += textwrap.wrap(f"{a.name} ({a.type}{optional}): {text}".rstrip(": "),
                                 WIDTH - 12, initial_indent="    ", subsequent_indent="        ")
    doc.append("Returns:")
    doc.append("    pd.DataFrame, GeoDataFrame, dict or GeoJSON depending on output_format."
               if table else "    dict: The response data.")
    out.append('        """')
    out += [f"        {l}".rstrip() for l in doc]
    out.append('        """')

    # Body
    path = op.path.lstrip("/")
    for a in args:
        if a.where == "path":
            path = path.replace("{" + a.key + "}", "{" + a.name + "}")
    out.append(f'        endpoint = f"{path}"' if "{" in path else f'        endpoint = "{path}"')

    def fill(var, items):
        if not items:
            return
        out.append(f"        {var} = {{}}")
        for a in items:
            if a.key == "lang":
                out.append(f'        {var}["lang"] = lang or self.lang')
            elif a.required:
                out.append(f'        {var}["{a.key}"] = {a.name}')
            else:
                out.append(f'        if {a.name} is not None:')
                out.append(f'            {var}["{a.key}"] = {a.name}')

    fill("params", query)
    if body and body[0].where == "payload":
        payload = body[0].name
    else:
        fill("payload", body)
        payload = "payload" if body else None
    fill("form", form)

    if query and op.method in ("POST", "PUT", "DELETE"):
        out.append("        if params:")
        out.append('            endpoint += "?" + urlencode(self._query_params(params), doseq=True)')
    if op.method == "GET":
        call = "_get_paged" if paged else "_get"
        out.append(f"        data = self.{call}(endpoint{', params=params' if query else ''})")
    elif op.method == "POST" and file_arg:
        out.append(f"        data = self._post_file(endpoint, {file_arg.name}{', payload=form' if form else ''})")
    elif op.method == "POST":
        out.append(f"        data = self._post(endpoint{', ' + payload if payload else ''})")
    elif op.method == "PUT":
        out.append(f"        data = self._put(endpoint{', ' + payload if payload else ''})")
    elif op.method == "PATCH":
        extra = f"{', ' + payload if payload else ', None'}{', params=params' if query else ''}"
        out.append(f"        data = self._patch(endpoint{extra})")
    elif op.method == "DELETE" and payload:
        out.append(f'        data = self._response_data("DELETE", endpoint, '
                   f'self._request("DELETE", endpoint, json={payload}))')
    else:
        out.append("        data = self._delete(endpoint)")
    if table:
        out.append(f"        return self._format_output(data{', crs=crs' if 'crs' in keys else ''})")
    else:
        out.append("        return data")
    return "\n".join(out)


def render_module(spec, ops, taken):
    """generated.py for the given missing operations."""
    methods, names = [], []
    for op in sorted(ops, key=lambda o: (o.path, o.method)):
        name = snake(op.operation_id)
        while name in taken:
            name += "_endpoint"
        taken.add(name)
        names.append((name, op))
        methods.append(render_method(spec, op, name))

    imports = []
    if any(op.method in ("POST", "PUT", "DELETE") and op.query for op in ops):
        imports.append("from urllib.parse import urlencode")
    if any(op.conceptual for op in ops):
        imports.append("from .base import conceptual")
    # The header names no URL, so the production and dev specs give the same
    # file whenever they have the same operations (--check stays meaningful).
    version = spec.get("info", {}).get("version", "?")
    header = (
        '"""API endpoints generated from the ScoutMaster OpenAPI spec.\n\n'
        "GENERATED by scripts/generate_endpoints.py -- do not edit by hand.\n\n"
        "Every spec operation that no hand-written method covers gets a method here.\n"
        "ScoutMasterAPI includes this class last, so hand-written methods always win:\n"
        "to improve a generated method, write a proper one in the right module and\n"
        "run the generator again; it then drops the generated one from this file.\n\n"
        f"Spec version: {version}\n"
        '"""\n'
    )
    parts = [header]
    if imports:
        parts.append("\n".join(imports) + "\n")
    count = f"{len(methods)} endpoint{'s' if len(methods) != 1 else ''}"
    parts.append(f"\n\nclass GeneratedEndpoints:\n    \"\"\"{count} without a hand-written method yet.\"\"\"\n")
    for m in methods:
        parts.append("\n" + m + "\n")
    return "".join(parts), names


# --- main --------------------------------------------------------------------------

def handwritten_client():
    """ScoutMasterAPI without the generated mixin."""
    if not OUTPUT.exists():  # api.py imports it; bootstrap an empty one
        OUTPUT.write_text(EMPTY_MODULE, encoding="utf-8", newline="\n")
    from scoutmasterapi_builder.api import ScoutMasterAPI
    from scoutmasterapi_builder.generated import GeneratedEndpoints
    bases = tuple(b for b in ScoutMasterAPI.__bases__ if b is not GeneratedEndpoints)
    return type("HandWrittenClient", bases, {})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    where = parser.add_mutually_exclusive_group()
    where.add_argument("--dev", action="store_true", help="use the dev API spec")
    where.add_argument("--spec", help="spec URL or local file (default: production)")
    parser.add_argument("--check", action="store_true",
                        help="don't write; exit 1 when generated.py is out of date")
    args = parser.parse_args(argv)

    source = args.spec or sc.SPEC_URLS["dev" if args.dev else "prod"]
    spec = sc.load_spec(source)
    ops = sc.spec_operations(spec)
    client = handwritten_client()
    calls, _ = sc.record_calls(client)
    missing = sc.missing_operations(ops, calls)
    taken = {n for n in dir(client) if not n.startswith("__")}
    code, names = render_module(spec, missing, taken)
    compile(code, str(OUTPUT), "exec")  # never write a file that doesn't parse

    current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
    print(f"Spec: {source} ({len(ops)} operations, {len(sc.EXCLUDED)} excluded on purpose)")
    if names:
        print(f"{len(names)} operation(s) without a hand-written method:")
        for name, op in names:
            print(f"  {name:45} {op.method:6} {op.path}{'  (conceptual)' if op.conceptual else ''}")
    else:
        print("Every operation has a hand-written method.")

    if args.check:
        if code != current:
            print(f"\n{OUTPUT.relative_to(REPO)} is out of date; run: python scripts/generate_endpoints.py")
            return 1
        print(f"\n{OUTPUT.relative_to(REPO)} is up to date.")
        return 0
    if code == current:
        print(f"\n{OUTPUT.relative_to(REPO)} unchanged.")
    else:
        OUTPUT.write_text(code, encoding="utf-8", newline="\n")
        print(f"\nWrote {OUTPUT.relative_to(REPO)}. Review it, run `pytest tests`, then commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
