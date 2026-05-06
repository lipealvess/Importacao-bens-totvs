import io
import re
import unicodedata
import zipfile
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

import pandas as pd
import streamlit as st


@dataclass(frozen=True)
class FieldSpec:
	key: str
	label: str
	kind: str
	required: bool


LAYOUTS = {
	"bens_patrimoniais": {
		"title": "Arquivo com Informacoes dos Bens Patrimoniais",
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
		"title": "Arquivo com Informacoes das Incorporacoes do Bem Patrimonial",
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
		"title": "Arquivo com Informacoes de Valores do Bem e Incorporacao",
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
		"title": "Arquivo com Informacoes de Alocacoes do Bem Patrimonial",
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
		"title": "Arquivo com Informacoes do Residual Minimo para Bens e Incorporacoes",
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


INT_ZERO_PAD_FIELDS = {
	"nro_sequencial_bem": 8,
	"bem_patrimonial": 9,
}


def format_int(value, field_key: str | None = None) -> str:
	if is_blank(value):
		return "0"
	text = str(value).strip().replace(" ", "")
	if text.endswith(",0"):
		text = text[:-2]
	if text.endswith(".0"):
		text = text[:-2]
	pad_size = INT_ZERO_PAD_FIELDS.get(field_key or "")
	if pad_size:
		numeric_text = text.replace(".", "").replace(",", "") if re.search(r"[\.,]\d{3}$", text) else text.replace(",", ".")
		if re.fullmatch(r"\d+(?:\.0+)?", numeric_text):
			numeric_text = re.sub(r"\.0+$", "", numeric_text)
			return numeric_text.zfill(pad_size)
	text = text.replace(".", "").replace(",", "") if re.search(r"[\.,]\d{3}$", text) else text.replace(",", ".")
	try:
		return str(int(Decimal(text)))
	except (InvalidOperation, ValueError):
		cleaned = re.sub(r"[^0-9-]", "", text)
		return cleaned or "0"


def format_alpha(value) -> str:
	if is_blank(value):
		return '""'
	text = str(value).strip().replace('"', "'")
	return f'"{text}"'


ALPHA_ZERO_PAD_FIELDS = {
	"estabelecimento": 2,
	"unid_negocio": 2,
}


def format_alpha_with_rules(value, field_key: str | None) -> str:
	if is_blank(value):
		return '""'

	text = str(value).strip().replace('"', "'")
	pad_size = ALPHA_ZERO_PAD_FIELDS.get(field_key or "")
	if pad_size:
		numeric_text = text.replace(" ", "")
		if re.fullmatch(r"\d+(?:[\.,]0+)?", numeric_text):
			numeric_text = re.sub(r"[\.,]0+$", "", numeric_text)
			text = numeric_text.zfill(pad_size)

	return f'"{text}"'


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


def format_value(value, kind: str, field_key: str | None = None) -> str:
	if kind == "int":
		return format_int(value, field_key)
	if kind == "alpha":
		return format_alpha_with_rules(value, field_key)
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

	totals: dict[str, Decimal] = {}
	for _, row in df.iterrows():
		bem = format_int(row[bem_col], "nro_sequencial_bem")
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


def build_field_aliases(field: FieldSpec) -> list[str]:
	aliases = {
		normalize_name(field.key),
		normalize_name(field.label),
		normalize_name(field.label.replace("/", " ")),
		normalize_name(field.label.replace("-", " ")),
	}

	replacements = {
		"nro": "numero",
		"nr": "numero",
		"num": "numero",
		"seq": "sequencia",
		"perc": "percentual",
		"qtd": "quantidade",
		"qtde": "quantidade",
		"dpr": "depreciacao",
		"incorp": "incorporacao",
		"docto": "documento",
		"ccusto": "centro_custo",
		"un": "unidade",
	}

	seed_aliases = list(aliases)
	for alias in seed_aliases:
		tokens = alias.split("_")
		expanded = [replacements.get(token, token) for token in tokens]
		aliases.add("_".join(expanded))

	return [a for a in aliases if a]


def resolve_column_mapping(df: pd.DataFrame, fields: list[FieldSpec]) -> dict[str, str | None]:
	normalized_to_original = {normalize_name(col): col for col in df.columns}
	resolved: dict[str, str | None] = {}

	for field in fields:
		match = None
		for candidate in build_field_aliases(field):
			if candidate in normalized_to_original:
				match = normalized_to_original[candidate]
				break
		resolved[field.key] = match

	return resolved


def generate_dat(
	df: pd.DataFrame,
	fields: list[FieldSpec],
	strict_required: bool,
	resolved_map: dict[str, str | None],
) -> tuple[str, list[str], list[str]]:
	missing_columns = []
	lines = []
	errors = []

	for field in fields:
		if resolved_map.get(field.key) is None and field.required:
			missing_columns.append(field.label)

	if strict_required and missing_columns:
		return "", missing_columns, []

	for row_number, row in df.iterrows():
		parts = []
		for field in fields:
			col = resolved_map.get(field.key)
			raw = row[col] if col is not None else None

			if strict_required and field.required and is_blank(raw):
				errors.append(f"Linha {row_number + 2}: campo obrigatorio ausente -> {field.label}")

			parts.append(format_value(raw, field.kind, field.key))

		lines.append(" ".join(parts))

	return "\n".join(lines) + "\n", missing_columns, errors


def mapping_preview(fields: list[FieldSpec], resolved_map: dict[str, str | None]) -> pd.DataFrame:
	return pd.DataFrame(
		{
			"campo_layout": [f.label for f in fields],
			"chave": [f.key for f in fields],
			"obrigatorio": ["sim" if f.required else "nao" for f in fields],
			"coluna_excel_mapeada": [resolved_map.get(f.key) or "(nao mapeada)" for f in fields],
		}
	)


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
		fields: list[FieldSpec] = layout_data["fields"]
		resolved_map = resolve_column_mapping(df, fields)
		dat_content, missing_columns, row_errors = generate_dat(df, fields, strict_required, resolved_map)

		if layout_key == "alocacoes":
			row_errors.extend(validate_alocacoes_percentuais(df, resolved_map))

		if missing_columns:
			missing_columns_by_layout[layout_data["title"]] = missing_columns
			continue

		if row_errors:
			errors_by_layout[layout_data["title"]] = row_errors
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


def app() -> None:
	st.set_page_config(page_title="Conversor Excel para DAT", layout="wide")
	st.title("Conversor de Excel para Arquivo DAT")
	st.caption("Layouts suportados: bens, incorporacoes, valores, alocacoes e residual minimo.")

	layout_key = st.selectbox(
		"Selecione o tipo de layout",
		options=list(LAYOUTS.keys()),
		format_func=lambda key: LAYOUTS[key]["title"],
	)

	layout = LAYOUTS[layout_key]
	fields: list[FieldSpec] = layout["fields"]

	col_a, col_b = st.columns([2, 1])
	with col_a:
		st.subheader("1) Suba o arquivo Excel")
		excel_file = st.file_uploader("Arquivo .xlsx ou .xls", type=["xlsx", "xls"])
	with col_b:
		st.subheader("2) Configuracao")
		strict_required = st.checkbox("Validar campos obrigatorios (bloqueia geracao)", value=True)

	st.subheader("Colunas esperadas no Excel")
	expected_df = pd.DataFrame(
		{
			"chave_coluna": [f.key for f in fields],
			"descricao": [f.label for f in fields],
			"tipo": [f.kind for f in fields],
			"obrigatorio": ["sim" if f.required else "nao" for f in fields],
		}
	)
	st.dataframe(expected_df, use_container_width=True, hide_index=True)

	template_df = build_template(fields)
	output_template = io.BytesIO()
	with pd.ExcelWriter(output_template, engine="openpyxl") as writer:
		template_df.to_excel(writer, index=False, sheet_name="dados")
	st.download_button(
		label="Baixar planilha modelo",
		data=output_template.getvalue(),
		file_name=f"template_{layout_key}.xlsx",
		mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	)

	if excel_file is None:
		st.info("Suba um arquivo Excel para gerar o DAT.")
		return

	try:
		file_bytes = excel_file.getvalue()
		df = pd.read_excel(io.BytesIO(file_bytes))
	except Exception as exc:
		st.error(f"Erro ao ler o Excel: {exc}")
		return

	st.subheader("Preview dos dados")
	st.caption(f"Arquivo carregado com {len(df)} linha(s). A tabela abaixo mostra apenas as primeiras 20 para conferencia.")
	st.dataframe(df.head(20), use_container_width=True)

	resolved_map = resolve_column_mapping(df, fields)

	st.subheader("Mapeamento de colunas (automatico)")
	st.dataframe(mapping_preview(fields, resolved_map), use_container_width=True, hide_index=True)

	with st.expander("Ajustar mapeamento manualmente (opcional)"):
		manual_map = {}
		options = [None] + list(df.columns)
		for field in fields:
			default_col = resolved_map.get(field.key)
			default_index = options.index(default_col) if default_col in options else 0
			selected = st.selectbox(
				f"{field.label} ({'obrigatorio' if field.required else 'opcional'})",
				options=options,
				index=default_index,
				key=f"map_{layout_key}_{field.key}",
			)
			manual_map[field.key] = selected

	use_manual_map = st.checkbox("Usar mapeamento manual acima", value=False)
	if use_manual_map:
		resolved_map = manual_map

	dat_content, missing_columns, row_errors = generate_dat(df, fields, strict_required, resolved_map)
	if layout_key == "alocacoes":
		row_errors.extend(validate_alocacoes_percentuais(df, resolved_map))

	if missing_columns:
		st.error("Colunas obrigatorias ausentes no Excel:")
		st.write(missing_columns)
		return

	if row_errors:
		st.error("Foram encontrados erros de validacao:")
		st.write(row_errors[:100])
		return

	st.success("Arquivo gerado com sucesso.")
	st.caption(f"O DAT foi gerado com {len(df)} linha(s), seguindo todas as linhas do Excel carregado.")
	col_utf8, col_ansi = st.columns(2)
	with col_utf8:
		st.download_button(
			label="Baixar arquivo DAT (UTF-8)",
			data=dat_content.encode("utf-8"),
			file_name=f"{layout_key}.dat",
			mime="text/plain",
		)
	with col_ansi:
		st.download_button(
			label="Baixar arquivo DAT (ANSI)",
			data=dat_content.encode("cp1252", errors="replace"),
			file_name=f"{layout_key}_ansi.dat",
			mime="text/plain",
		)

	st.subheader("Preview do DAT")
	st.caption("O preview abaixo mostra apenas as primeiras 10 linhas do arquivo gerado.")
	st.code("\n".join(dat_content.splitlines()[:10]), language="text")

	st.divider()
	st.subheader("Geracao em lote dos 5 layouts")
	st.caption(
		"Para gerar todos de uma vez, use um Excel com abas separadas nomeadas como: "
		"bens_patrimoniais, incorporacoes, valores, alocacoes e residual_minimo."
	)

	if st.button("Gerar ZIP com os 5 layouts (UTF-8 + ANSI)"):
		try:
			dat_by_layout, missing_sheets, missing_columns_by_layout, errors_by_layout = generate_all_layouts_from_workbook(
				file_bytes,
				strict_required,
			)
		except Exception as exc:
			st.error(f"Erro na geracao em lote: {exc}")
			return

		if missing_sheets:
			st.error("Abas ausentes no Excel para geracao em lote:")
			st.write(missing_sheets)

		if missing_columns_by_layout:
			st.error("Colunas obrigatorias ausentes em alguns layouts:")
			st.write(missing_columns_by_layout)

		if errors_by_layout:
			st.error("Erros de validacao encontrados em alguns layouts:")
			st.write({k: v[:20] for k, v in errors_by_layout.items()})

		if dat_by_layout:
			zip_bytes = build_zip_with_layouts(dat_by_layout)
			st.success(f"Gerados {len(dat_by_layout)} layout(s) com sucesso.")
			st.download_button(
				label="Baixar ZIP dos layouts gerados",
				data=zip_bytes,
				file_name="layouts_dat_utf8_ansi.zip",
				mime="application/zip",
			)


if __name__ == "__main__":
	app()
