from app.services.file_service import extract_text



arquivo = "C:/temp/aula_funcoes.pdf"


texto = extract_text(
    arquivo
)


print("====================")
print("TEXTO EXTRAÍDO")
print("====================")


print(texto[:2000])