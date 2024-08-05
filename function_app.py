import logging
import azure.functions as func
from azure.functions.decorators.core import DataType
import uuid
# Follow this microsoft learn doc to add azure SQL Server credentials 
# https://learn.microsoft.com/en-us/azure/azure-functions/functions-add-output-binding-azure-sql-vs-code?pivots=programming-language-python
app = func.FunctionApp()

@app.function_name(name="HttpTrigger")
@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
@app.generic_output_binding(arg_name="controls", type="sql", CommandText="dbo.Controls", ConnectionStringSetting="SqlConnectionString", data_type=DataType.STRING)
def test_function(req: func.HttpRequest, controls: func.Out[func.SqlRow]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    value = req.params.get('value')
    record_id = req.params.get('id')

    if not value or not record_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            value = req_body.get('value')
            record_id = req_body.get('id')

    if value is None or record_id is None:
        return func.HttpResponse(
            "Por favor, proporciona 'id' y 'value' en la URL usando ?id=<id>&value=1 o ?id=<id>&value=0.",
            status_code=400
        )

    if value in ['0', '1']:
        controls.set(func.SqlRow({"id": record_id, "status": value}))
        return func.HttpResponse(f"El valor {value} ha sido guardado en la base de datos con id {record_id}.")
    else:
        return func.HttpResponse(
            "El valor debe ser '1' o '0'.",
            status_code=400
        )
