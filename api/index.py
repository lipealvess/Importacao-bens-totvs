import io
import re
import unicodedata
import zipfile
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

import pandas as pd
from flask import Flask, Response, request

app = Flask(__name__)


@dataclass(frozen=True)
class FieldSpec:
    key: str
    label: str
    kind: str
    required: bool


LAYOUTS = {
    "bens_patrimoniais": {
        "title": "Bens Patrimoniais",
        "fields": [
            FieldSpec("nro_sequencial_bem", "Nro Sequencial Bem", "int", True),
            FieldSpec("empresa", "Empresa", "alpha", True),
            FieldSpec("conta_patrimonial", "Conta Patrimonial", "alpha", True),
            FieldSpec("bem_patrimonial", "Bem Patrimonial", "int", True),
            FieldSpec("sequencia_bem", "Sequencia Bem", "int", True),
            FieldSpec("descricao_bem_pat", "Descricao Bem Pat", "alpha", True),
            FieldSpec("numero_plaqueta", "Numero Plaqueta", "alpha", True),
            FieldSpec("quantidade_bens_representados", "Quantidade Bens Representados", "int", True),
            FieldSpec("periodicidade", "Periodicidade", "alpha", True),
            FieldSpec("data_aquisicao", "Data Aquisicao", "date", True),
            FieldSpec("estabelecimento", "Estabelecimento", "alpha", True),
            FieldSpec("especie_bem_patrimonial", "Especie Bem Patrimonial", "alpha", False),
            FieldSpec("marca", "Marca", "alpha", False),
            FieldSpec("modelo", "Modelo", "alpha", False),
            FieldSpec("licenca_uso", "Licenca Uso", "alpha", False),
            FieldSpec("especificacao_tecnica", "Especificacao Tecnica", "alpha", False),
            FieldSpec("estado_fisico", "Estado Fisico", "alpha", False),
            FieldSpec("arrendador", "Arrendador", "alpha", False),
            FieldSpec("contrato_leasing", "Contrato Leasing", "alpha", False),
            FieldSpec("fornecedor", "Fornecedor", "int", False),
            FieldSpec("localizacao", "Localizacao", "alpha", False),
            FieldSpec("responsavel", "Responsavel", "alpha", False),
            FieldSpec("ultimo_inventario", "Ultimo Inventario", "date", False),
            FieldSpec("narrativa_bem", "Narrativa Bem", "alpha", False),
            FieldSpec("seguradora", "Seguradora", "alpha", False),
            FieldSpec("apolice_seguro", "Apolice Seguro", "alpha", False),
            FieldSpec("inicio_valid_apolice", "Inicio Valid Apolice", "date", False),
            FieldSpec("fim_validade_apolice", "Fim Validade Apolice", "date", False),
            FieldSpec("premio_seguro", "Premio Seguro", "dec2", False),
            FieldSpec("seguradora_1", "Seguradora 1", "alpha", False),
            FieldSpec("apolice_seguro_1", "Apolice Seguro 1", "alpha", False),
            FieldSpec("inicio_valid_apolice_1", "Inicio Valid Apolice 1", "date", False),
            FieldSpec("fim_validade_apolice_1", "Fim Validade Apolice 1", "date", False),
            FieldSpec("premio_seguro_1", "Premio Seguro 1", "dec2", False),
            FieldSpec("seguradora_2", "Seguradora 2", "alpha", False),
            FieldSpec("apolice_seguro_2", "Apolice Seguro 2", "alpha", False),
            FieldSpec("inicio_valid_apolice_2", "Inicio Valid Apolice 2", "date", False),
            FieldSpec("fim_validade_apolice_2", "Fim Validade Apolice 2", "date", False),
            FieldSpec("premio_seguro_2", "Premio Seguro 2", "dec2", False),
            FieldSpec("docto_entrada", "Docto Entrada", "alpha", False),
            FieldSpec("numero_item", "Numero Item", "int", False),
            FieldSpec("pessoa_garantia", "Pessoa Garantia", "int", False),
            FieldSpec("inicio_garantia", "Inicio Garantia", "date", False),
            FieldSpec("fim_garantia", "Fim Garantia", "date", False),
            FieldSpec("termo_garantia", "Termo Garantia", "alpha", False),
            FieldSpec("grupo_calculo", "Grupo Calculo", "alpha", False),
            FieldSpec("data_movimento", "Data Movimento", "date", False),
            FieldSpec("perc_baixado", "Perc Baixado", "dec2", False),
            FieldSpec("inicio_calculo_dpr", "Inicio Calculo Dpr", "date", False),
            FieldSpec("data_calculo", "Data Calculo", "date", False),
            FieldSpec("serie_nota", "Serie Nota", "alpha", False),
            FieldSpec("bem_importado", "Bem Importado", "yesno", True),
            FieldSpec("credita_pis", "Credita PIS", "yesno", True),
            FieldSpec("credita_cofins", "Credita COFINS", "yesno", True),
            FieldSpec("nro_parcelas_credito_pis_cofins", "Nro Parcelas Credito PIS COFINS", "int", True),
            FieldSpec("parcelas_descontadas", "Parcelas Descontadas", "int", True),
            FieldSpec("valor_credito_pis", "Valor Credito PIS", "dec2", False),
            FieldSpec("valor_credito_cofins", "Valor Credito COFINS", "dec2", False),
            FieldSpec("credita_csll", "Credita CSLL", "yesno", True),
            FieldSpec("exercicios_credito_csll", "Exercicios Credito CSLL", "int", True),
            FieldSpec("valor_base_pis", "Valor Base PIS", "dec2", False),
            FieldSpec("valor_base_cofins", "Valor Base COFINS", "dec2", False),
            FieldSpec("natureza_operacao", "Natureza Operacao", "alpha", False),
            FieldSpec("valor_exclusao_icms", "Valor Exclusao ICMS", "dec2", False),
        ],
    },
    "incorporacoes": {
        "title": "Incorporacoes",
        "fields": [
            FieldSpec("nro_sequencial_bem", "Nro Sequencial Bem", "int", True),
            FieldSpec("sequencia_incorp", "Sequencia Incorp", "int", True),
            FieldSpec("cenario_contabil", "Cenario Contabil", "alpha", False),
            FieldSpec("tipo_incorporacao", "Tipo Incorporacao", "alpha", True),
            FieldSpec("data_incorporacao", "Data Incorporacao", "date", True),
            FieldSpec("descricao_incorp", "Descricao Incorp", "alpha", True),
            FieldSpec("finalidade", "Finalidade", "alpha", True),
            FieldSpec("incentivo_fiscal", "Incentivo Fiscal", "alpha", False),
            FieldSpec("fornecedor", "Fornecedor", "int", False),
            FieldSpec("docto_entrada", "Docto Entrada", "alpha", False),
            FieldSpec("numero_item", "Numero Item", "int", False),
            FieldSpec("tipo_calculo_reaval", "Tipo Calculo Reaval", "alpha", False),
            FieldSpec("percentual_anual", "Percentual Anual", "dec3", False),
            FieldSpec("perc_anual_dpr_incen", "Perc Anual Dpr Incen", "dec3", False),
            FieldSpec("conta_patrimonial", "Conta Patrimonial", "alpha", False),
            FieldSpec("percentual_anual_reducao_saldo", "Percentual Anual Reducao Saldo", "dec3", False),
            FieldSpec("valor_credito_pis", "Valor Credito PIS", "dec2", False),
            FieldSpec("valor_credito_cofins", "Valor Credito COFINS", "dec2", False),
            FieldSpec("bem_importado", "Bem Importado", "yesno", True),
            FieldSpec("credita_pis", "Credita PIS", "yesno", True),
            FieldSpec("credita_cofins", "Credita COFINS", "yesno", True),
            FieldSpec("nro_parcelas_credito_pis_cofins", "Nro Parcelas Credito PIS COFINS", "int", True),
            FieldSpec("parcelas_descontadas", "Parcelas Descontadas", "int", True),
            FieldSpec("credito_csll", "Credito CSLL", "yesno", True),
            FieldSpec("exercicios_credito_csll", "Exercicios Credito CSLL", "int", True),
            FieldSpec("serie_nota", "Serie Nota", "alpha", False),
            FieldSpec("qtde_item_docto", "Qtde Item Docto", "int", False),
            FieldSpec("valor_base_pis", "Valor Base PIS", "dec2", False),
            FieldSpec("valor_base_cofins", "Valor Base COFINS", "dec2", False),
            FieldSpec("natureza_operacao", "Natureza Operacao", "alpha", False),
            FieldSpec("valor_exclusao_icms", "Valor Exclusao ICMS", "dec2", False),
        ],
    },
    "valores": {
        "title": "Valores",
        "fields": [
            FieldSpec("nro_sequencial_bem", "Nro Sequencial Bem", "int", True),
            FieldSpec("sequencia_incorp", "Sequencia Incorp", "int", False),
            FieldSpec("cenario_contabil", "Cenario Contabil", "alpha", True),
            FieldSpec("finalidade", "Finalidade", "alpha", True),
            FieldSpec("valor_original", "Valor Original", "dec2", True),
            FieldSpec("correcao_monetaria", "Correcao Monetaria", "dec2", False),
            FieldSpec("dpr_valor_original", "Dpr Valor Original", "dec2", False),
            FieldSpec("dpr_correcao_monet", "Dpr Correcao Monet", "dec2", False),
            FieldSpec("correcao_monet_dpr", "Correcao Monet Dpr", "dec2", False),
            FieldSpec("depreciacao_incentiv", "Depreciacao Incentiv", "dec2", False),
            FieldSpec("dpr_incentiv_cm", "Dpr Incentiv CM", "dec2", False),
            FieldSpec("cm_dpr_incentivada", "CM Dpr Incentivada", "dec2", False),
            FieldSpec("amortizacao_vo", "Amortizacao VO", "dec2", False),
            FieldSpec("amortizacao_cm", "Amortizacao CM", "dec2", False),
            FieldSpec("cm_amortizacao", "CM Amortizacao", "dec2", False),
            FieldSpec("amortizacao_incentiv", "Amortizacao Incentiv", "dec2", False),
            FieldSpec("amort_incentiv_cm", "Amort Incentiv CM", "dec2", False),
            FieldSpec("cm_amort_incentvda", "CM Amort Incentvda", "dec2", False),
            FieldSpec("percentual_dpr", "Percentual Dpr", "dec4", False),
            FieldSpec("perc_dpr_incentivada", "Perc Dpr Incentivada", "dec4", False),
            FieldSpec("perc_dpr_reducao_saldo", "Perc Dpr Reducao Saldo", "dec4", False),
            FieldSpec("quantidade_vida_util", "Quantidade Vida Util", "dec2", False),
        ],
    },
    "alocacoes": {
        "title": "Alocacoes",
        "fields": [
            FieldSpec("nro_sequencial_bem", "Nro Sequencial Bem", "int", True),
            FieldSpec("plano_centros_custo", "Plano Centros Custo", "alpha", True),
            FieldSpec("centro_custo", "Centro Custo", "alpha", True),
            FieldSpec("unid_negocio", "Unid Negocio", "alpha", True),
            FieldSpec("perc_apropriacao", "Perc Apropriacao", "dec4", True),
            FieldSpec("ccusto_un_principal", "CCusto UN Principal", "yesno", True),
        ],
    },
    "residual_minimo": {
        "title": "Residual Minimo",
        "fields": [
            FieldSpec("nro_sequencial_bem", "Nro Sequencial Bem", "int", True),
            FieldSpec("sequencia_incorp", "Sequencia Incorp", "int", True),
            FieldSpec("tipo_calculo", "Tipo Calculo", "alpha", True),
            FieldSpec("cenario_contabil", "Cenario Contabil", "alpha", True),
            FieldSpec("finalidade_economica", "Finalidade Economica", "alpha", True),
            FieldSpec("residual_minimo", "Residual Minimo", "dec2", True),
        ],
    },
}


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return re.sub(r"_+", "_", value).strip("_")


def is_blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    text = str(value).strip()
    return text == "" or text.lower() in {"nan", "none"}


def format_int(value) -> str:
    if is_blank(value):
        return "0"
    text = str(value).strip().replace(" ", "")
    if text.endswith(",0"):
        text = text[:-2]
    if text.endswith(".0"):
        text = text[:-2]
    try:
        return str(int(Decimal(text.replace(",", "."))))
    except (InvalidOperation, ValueError):
        cleaned = re.sub(r"[^0-9-]", "", text)
        return cleaned or "0"


def format_alpha(value) -> str:
    if is_blank(value):
        return '""'
    return f'"{str(value).strip().replace(chr(34), chr(39))}"'


def format_yesno(value) -> str:
    if is_blank(value):
        return "NO"
    text = str(value).strip().lower()
    if text in {"yes", "y", "sim", "s", "1", "true"}:
        return "YES"
    if text in {"no", "n", "nao", "não", "0", "false"}:
        return "NO"
    return "YES" if text.startswith("y") else "NO"


def format_date(value) -> str:
    if is_blank(value):
        return "?"
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.strftime("%d/%m/%Y")
    text = str(value).strip()
    if text == "?":
        return "?"
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return text


def format_decimal(value, places: int) -> str:
    if is_blank(value):
        quant = Decimal("1").scaleb(-places)
        return f"{Decimal('0').quantize(quant)}".replace(".", ",")

    text = str(value).strip().replace(" ", "")
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    else:
        text = text.replace(",", ".")

    try:
        number = Decimal(text)
    except InvalidOperation:
        number = Decimal("0")

    quant = Decimal("1").scaleb(-places)
    return f"{number.quantize(quant)}".replace(".", ",")


def format_value(value, kind: str) -> str:
    if kind == "int":
        return format_int(value)
    if kind == "alpha":
        return format_alpha(value)
    if kind == "yesno":
        return format_yesno(value)
    if kind == "date":
        return format_date(value)
    if kind == "dec2":
        return format_decimal(value, 2)
    if kind == "dec3":
        return format_decimal(value, 3)
    if kind == "dec4":
        return format_decimal(value, 4)
    return str(value)


def build_field_aliases(field: FieldSpec) -> list[str]:
    aliases = {
        normalize_name(field.key),
        normalize_name(field.label),
    }
    replacements = {
        "nro": "numero",
        "seq": "sequencia",
        "perc": "percentual",
        "qtde": "quantidade",
        "incorp": "incorporacao",
        "docto": "documento",
    }
    seed_aliases = list(aliases)
    for alias in seed_aliases:
        tokens = alias.split("_")
        expanded = [replacements.get(token, token) for token in tokens]
        aliases.add("_".join(expanded))
    return [a for a in aliases if a]


def resolve_column_mapping(df: pd.DataFrame, fields: list[FieldSpec]) -> dict[str, str | None]:
    normalized_to_original = {normalize_name(col): col for col in df.columns}
    resolved = {}
    for field in fields:
        match = None
        for candidate in build_field_aliases(field):
            if candidate in normalized_to_original:
                match = normalized_to_original[candidate]
                break
        resolved[field.key] = match
    return resolved


def parse_decimal_value(value) -> Decimal:
    if is_blank(value):
        return Decimal("0")
    text = str(value).strip().replace(" ", "")
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    else:
        text = text.replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation:
        return Decimal("0")


def validate_alocacoes_percentuais(df: pd.DataFrame, resolved_map: dict[str, str | None]) -> list[str]:
    bem_col = resolved_map.get("nro_sequencial_bem")
    perc_col = resolved_map.get("perc_apropriacao")
    if bem_col is None or perc_col is None:
        return []

    totals = {}
    for _, row in df.iterrows():
        bem = format_int(row[bem_col])
        perc = parse_decimal_value(row[perc_col])
        totals[bem] = totals.get(bem, Decimal("0")) + perc

    errors = []
    tolerance = Decimal("0.01")
    for bem, total in totals.items():
        if abs(total - Decimal("100")) > tolerance:
            errors.append(
                f"Soma dos percentuais apropriados do bem {bem} difere de 100% (total calculado: {str(total).replace('.', ',')})"
            )
    return errors


def generate_dat(df: pd.DataFrame, layout_key: str, strict_required: bool) -> tuple[str, list[str]]:
    fields = LAYOUTS[layout_key]["fields"]
    resolved_map = resolve_column_mapping(df, fields)
    errors = []

    missing_columns = [f.label for f in fields if f.required and resolved_map.get(f.key) is None]
    if strict_required and missing_columns:
        return "", [f"Colunas obrigatorias ausentes: {', '.join(missing_columns)}"]

    if layout_key == "alocacoes":
        errors.extend(validate_alocacoes_percentuais(df, resolved_map))

    lines = []
    for row_number, row in df.iterrows():
        parts = []
        for field in fields:
            col = resolved_map.get(field.key)
            raw = row[col] if col is not None else None
            if strict_required and field.required and is_blank(raw):
                errors.append(f"Linha {row_number + 2}: campo obrigatorio ausente -> {field.label}")
            parts.append(format_value(raw, field.kind))
        lines.append(" ".join(parts))

    if errors:
        return "", errors

    return "\n".join(lines) + "\n", []


def build_template(fields: list[FieldSpec]) -> pd.DataFrame:
    data = {field.key: [""] for field in fields}
    return pd.DataFrame(data)


def find_sheet_for_layout(sheet_names: list[str], layout_key: str) -> str | None:
    aliases = {
        "bens_patrimoniais": {
            "bens_patrimoniais",
            "bens",
            "informacoes_dos_bens_patrimoniais",
        },
        "incorporacoes": {
            "incorporacoes",
            "incorporacoes_bem_patrimonial",
            "informacoes_das_incorporacoes_do_bem_patrimonial",
        },
        "valores": {
            "valores",
            "valores_bem_incorporacao",
            "informacoes_de_valores_do_bem_e_incorporacao",
        },
        "alocacoes": {
            "alocacoes",
            "alocacoes_bem_patrimonial",
            "informacoes_de_alocacoes_do_bem_patrimonial",
        },
        "residual_minimo": {
            "residual_minimo",
            "residual",
            "residual_minimo_bens_incorporacoes",
            "informacoes_do_residual_minimo_para_bens_e_incorporacoes",
        },
    }

    normalized = {normalize_name(name): name for name in sheet_names}
    for alias in aliases.get(layout_key, {layout_key}):
        if alias in normalized:
            return normalized[alias]
    return None


def generate_all_layouts_from_workbook(
    file_bytes: bytes,
    strict_required: bool,
) -> tuple[dict[str, str], list[str], dict[str, list[str]], dict[str, list[str]]]:
    book = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
    dat_by_layout: dict[str, str] = {}
    missing_sheets: list[str] = []
    missing_columns_by_layout: dict[str, list[str]] = {}
    errors_by_layout: dict[str, list[str]] = {}

    for layout_key, layout_data in LAYOUTS.items():
        sheet_name = find_sheet_for_layout(list(book.keys()), layout_key)
        if not sheet_name:
            missing_sheets.append(layout_data["title"])
            continue

        df = book[sheet_name]
        dat_content, errors = generate_dat(df, layout_key, strict_required)

        missing_errors = [e for e in errors if e.startswith("Colunas obrigatorias ausentes")]
        other_errors = [e for e in errors if e not in missing_errors]

        if missing_errors:
            missing_columns_by_layout[layout_data["title"]] = missing_errors
            continue

        if other_errors:
            errors_by_layout[layout_data["title"]] = other_errors
            continue

        dat_by_layout[layout_key] = dat_content

    return dat_by_layout, missing_sheets, missing_columns_by_layout, errors_by_layout


def build_zip_with_layouts(dat_by_layout: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for layout_key, dat_content in dat_by_layout.items():
            zf.writestr(f"{layout_key}.dat", dat_content.encode("utf-8"))
            zf.writestr(f"{layout_key}_ansi.dat", dat_content.encode("cp1252", errors="replace"))
    buffer.seek(0)
    return buffer.getvalue()


def layout_metadata() -> dict[str, dict]:
    meta = {}
    for key, data in LAYOUTS.items():
        fields = data["fields"]
        meta[key] = {
            "title": data["title"],
            "fields": [
                {
                    "key": f.key,
                    "label": f.label,
                    "type": f.kind,
                    "required": f.required,
                }
                for f in fields
            ],
        }
    return meta


@app.get("/")
def index() -> Response:
    options = "".join([f'<option value="{k}">{v["title"]}</option>' for k, v in LAYOUTS.items()])
    meta = layout_metadata()
    html = f"""
    <!doctype html>
    <html lang='pt-br'>
    <head>
      <meta charset='utf-8'>
      <meta name='viewport' content='width=device-width, initial-scale=1'>
      <title>Conversor Excel para DAT</title>
      <style>
                :root {{
                    --bg: #f4f7fb;
                    --card: #ffffff;
                    --ink: #14213d;
                    --sub: #5c677d;
                    --line: #d9e2ec;
                    --brand: #0b6e4f;
                    --brand2: #148a66;
                    --danger: #b42318;
                }}
                * {{ box-sizing: border-box; }}
                body {{
                    margin: 0;
                    font-family: "Segoe UI", "Helvetica Neue", sans-serif;
                    color: var(--ink);
                    background:
                        radial-gradient(circle at 15% 20%, #d7f4ea 0, transparent 25%),
                        radial-gradient(circle at 90% 10%, #e7f0ff 0, transparent 28%),
                        var(--bg);
                }}
                .wrap {{ max-width: 1120px; margin: 28px auto; padding: 0 16px; }}
                .hero {{
                    background: linear-gradient(135deg, #0b6e4f, #167f5f);
                    color: white;
                    border-radius: 16px;
                    padding: 24px;
                    box-shadow: 0 10px 30px rgba(11, 110, 79, .25);
                    margin-bottom: 16px;
                }}
                .hero h1 {{ margin: 0 0 8px; font-size: 26px; }}
                .hero p {{ margin: 0; opacity: .95; }}
                .grid {{ display: grid; grid-template-columns: 1.2fr .8fr; gap: 16px; }}
                @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} }}
                .card {{
                    background: var(--card);
                    border: 1px solid var(--line);
                    border-radius: 14px;
                    padding: 16px;
                    box-shadow: 0 6px 20px rgba(20, 33, 61, .06);
                }}
                h2 {{ margin: 4px 0 12px; font-size: 19px; }}
                h3 {{ margin: 4px 0 10px; font-size: 16px; }}
                label {{ display: block; margin-top: 10px; font-weight: 600; }}
                input, select {{
                    width: 100%;
                    padding: 10px 11px;
                    margin-top: 6px;
                    border: 1px solid var(--line);
                    border-radius: 10px;
                    background: white;
                }}
                .row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
                .row3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
                @media (max-width: 700px) {{ .row, .row3 {{ grid-template-columns: 1fr; }} }}
                .actions {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }}
                button, .btn {{
                    border: 0;
                    border-radius: 10px;
                    padding: 10px 13px;
                    background: var(--brand);
                    color: white;
                    font-weight: 600;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                }}
                .btn.secondary {{ background: #334155; }}
                .btn.light {{ background: #edf7f3; color: #0a5b41; border: 1px solid #b8e3d4; }}
                .hint {{ color: var(--sub); font-size: 13px; margin-top: 8px; }}
                .msg {{
                    margin-top: 12px;
                    padding: 11px;
                    border-radius: 10px;
                    font-size: 14px;
                    white-space: pre-wrap;
                    border: 1px solid var(--line);
                    background: #f8fafc;
                }}
                .msg.error {{ border-color: #fecaca; background: #fef2f2; color: var(--danger); }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
                th, td {{ border-bottom: 1px solid var(--line); padding: 8px 6px; text-align: left; }}
                th {{ background: #f8fafc; }}
                .badge {{ padding: 2px 8px; border-radius: 999px; font-size: 12px; }}
                .req {{ background: #fee2e2; color: #991b1b; }}
                .opt {{ background: #e2e8f0; color: #334155; }}
                .muted {{ color: var(--sub); font-size: 13px; }}
      </style>
    </head>
    <body>
            <div class='wrap'>
                <section class='hero'>
                    <h1>Conversor Excel para DAT</h1>
                    <p>Migracao SoulMV para TOTVS Datasul com validacao e exportacao em UTF-8 e ANSI.</p>
                </section>

                <section class='grid'>
                    <div class='card'>
                        <h2>Conversao Individual</h2>
                        <form id='singleForm'>
                            <div class='row'>
                                <div>
                                    <label>Layout</label>
                                    <select id='layout_key' name='layout_key'>{options}</select>
                                </div>
                                <div>
                                    <label>Codificacao</label>
                                    <select name='encoding'>
                                        <option value='utf-8'>UTF-8</option>
                                        <option value='cp1252'>ANSI (Windows-1252)</option>
                                    </select>
                                </div>
                            </div>

                            <label>Arquivo Excel (.xlsx/.xls)</label>
                            <input type='file' name='excel_file' accept='.xlsx,.xls' required>

                            <label><input type='checkbox' name='strict_required' checked> Validar campos obrigatorios</label>

                            <div class='actions'>
                                <button type='submit'>Gerar DAT</button>
                                <a class='btn light' id='templateLink' href='/template?layout_key=bens_patrimoniais'>Baixar template do layout</a>
                            </div>
                            <div class='hint'>Mostra erro detalhado quando faltar campo obrigatorio ou regra de alocacao nao fechar 100%.</div>
                            <div id='singleMsg' class='msg' style='display:none;'></div>
                        </form>
                    </div>

                    <div class='card'>
                        <h2>Geracao em Lote</h2>
                        <h3>ZIP com 5 layouts</h3>
                        <form id='batchForm'>
                            <label>Excel com abas (bens_patrimoniais, incorporacoes, valores, alocacoes, residual_minimo)</label>
                            <input type='file' name='excel_file' accept='.xlsx,.xls' required>
                            <label><input type='checkbox' name='strict_required' checked> Validar campos obrigatorios</label>
                            <div class='actions'>
                                <button type='submit'>Gerar ZIP (UTF-8 + ANSI)</button>
                            </div>
                            <div class='hint'>Gera apenas os layouts validos e lista pendencias por aba.</div>
                            <div id='batchMsg' class='msg' style='display:none;'></div>
                        </form>
                    </div>
                </section>

                <section class='card' style='margin-top:16px;'>
                    <h2>Campos Esperados do Layout</h2>
                    <p class='muted'>Tabela muda automaticamente conforme o layout selecionado.</p>
                    <table>
                        <thead><tr><th>Chave</th><th>Descricao</th><th>Tipo</th><th>Obrigatorio</th></tr></thead>
                        <tbody id='fieldsTable'></tbody>
                    </table>
                </section>
      </div>

            <script>
                const META = {meta};
                const layoutSelect = document.getElementById('layout_key');
                const fieldsTable = document.getElementById('fieldsTable');
                const templateLink = document.getElementById('templateLink');

                function escapeHtml(text) {{
                    return String(text)
                        .replace(/&/g, '&amp;')
                        .replace(/</g, '&lt;')
                        .replace(/>/g, '&gt;')
                        .replace(/"/g, '&quot;')
                        .replace(/'/g, '&#039;');
                }}

                function renderFields() {{
                    const key = layoutSelect.value;
                    templateLink.href = '/template?layout_key=' + encodeURIComponent(key);
                    const fields = META[key].fields;
                    fieldsTable.innerHTML = fields.map(f => `
                        <tr>
                            <td>${{escapeHtml(f.key)}}</td>
                            <td>${{escapeHtml(f.label)}}</td>
                            <td>${{escapeHtml(f.type)}}</td>
                            <td><span class="badge ${{f.required ? 'req' : 'opt'}}">${{f.required ? 'sim' : 'nao'}}</span></td>
                        </tr>
                    `).join('');
                }}

                function showMessage(el, text, isError) {{
                    el.style.display = 'block';
                    el.className = isError ? 'msg error' : 'msg';
                    el.textContent = text;
                }}

                async function submitFileForm(formId, url, msgId, downloadName) {{
                    const form = document.getElementById(formId);
                    const msg = document.getElementById(msgId);
                    form.addEventListener('submit', async (e) => {{
                        e.preventDefault();
                        showMessage(msg, 'Processando arquivo...', false);

                        const data = new FormData(form);
                        const response = await fetch(url, {{ method: 'POST', body: data }});
                        if (!response.ok) {{
                            const errorText = await response.text();
                            showMessage(msg, errorText || 'Erro na operacao.', true);
                            return;
                        }}

                        const blob = await response.blob();
                        const contentDisposition = response.headers.get('content-disposition') || '';
                        const match = contentDisposition.match(/filename="?([^";]+)"?/i);
                        const fileName = match ? match[1] : downloadName;

                        const a = document.createElement('a');
                        a.href = URL.createObjectURL(blob);
                        a.download = fileName;
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                        showMessage(msg, 'Arquivo gerado com sucesso.', false);
                    }});
                }}

                layoutSelect.addEventListener('change', renderFields);
                renderFields();
                submitFileForm('singleForm', '/convert', 'singleMsg', 'layout.dat');
                submitFileForm('batchForm', '/convert-all', 'batchMsg', 'layouts_dat_utf8_ansi.zip');
            </script>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")


@app.get("/template")
def template() -> Response:
        layout_key = request.args.get("layout_key", "")
        if layout_key not in LAYOUTS:
                return Response("Layout invalido.", status=400)

        output = io.BytesIO()
        df = build_template(LAYOUTS[layout_key]["fields"])
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="dados")
        output.seek(0)

        headers = {
                "Content-Disposition": f'attachment; filename="template_{layout_key}.xlsx"'
        }
        return Response(
                output.getvalue(),
                status=200,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers=headers,
        )


@app.post("/convert")
def convert() -> Response:
    if "excel_file" not in request.files:
        return Response("Arquivo Excel nao enviado.", status=400)

    excel = request.files["excel_file"]
    layout_key = request.form.get("layout_key", "")
    encoding = request.form.get("encoding", "utf-8")
    strict_required = request.form.get("strict_required") is not None

    if layout_key not in LAYOUTS:
        return Response("Layout invalido.", status=400)

    try:
        df = pd.read_excel(io.BytesIO(excel.read()))
    except Exception as exc:
        return Response(f"Erro ao ler o Excel: {exc}", status=400)

    dat_content, errors = generate_dat(df, layout_key, strict_required)
    if errors:
        return Response("\n".join(errors), status=400, mimetype="text/plain")

    try:
        payload = dat_content.encode(encoding, errors="replace")
    except Exception as exc:
        return Response(f"Erro de codificacao: {exc}", status=400)

    file_suffix = "ansi" if encoding == "cp1252" else "utf8"
    headers = {
        "Content-Disposition": f'attachment; filename="{layout_key}_{file_suffix}.dat"'
    }
    return Response(payload, status=200, mimetype="text/plain", headers=headers)


@app.post("/convert-all")
def convert_all() -> Response:
    if "excel_file" not in request.files:
        return Response("Arquivo Excel nao enviado.", status=400)

    excel = request.files["excel_file"]
    strict_required = request.form.get("strict_required") is not None

    try:
        file_bytes = excel.read()
        dat_by_layout, missing_sheets, missing_columns_by_layout, errors_by_layout = generate_all_layouts_from_workbook(
            file_bytes,
            strict_required,
        )
    except Exception as exc:
        return Response(f"Erro na geracao em lote: {exc}", status=400)

    messages = []
    if missing_sheets:
        messages.append("Abas ausentes: " + ", ".join(missing_sheets))
    if missing_columns_by_layout:
        messages.append("Colunas obrigatorias ausentes por layout: " + str(missing_columns_by_layout))
    if errors_by_layout:
        messages.append("Erros de validacao por layout: " + str(errors_by_layout))

    if not dat_by_layout:
        msg = "Nenhum layout foi gerado.\n" + "\n".join(messages)
        return Response(msg.strip(), status=400, mimetype="text/plain")

    zip_bytes = build_zip_with_layouts(dat_by_layout)
    headers = {
        "Content-Disposition": 'attachment; filename="layouts_dat_utf8_ansi.zip"'
    }
    if messages:
        headers["X-Conversion-Warnings"] = " | ".join(messages)[:1500]

    return Response(zip_bytes, status=200, mimetype="application/zip", headers=headers)
