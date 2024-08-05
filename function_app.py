import json
import logging
import azure.functions as func
from azure.functions.decorators.core import DataType

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
    
# Función para obtener valores de la base de datos
@app.function_name(name="GetValue")
@app.route(route="get_value", auth_level=func.AuthLevel.FUNCTION)
@app.sql_input(arg_name="control", command_text="SELECT [id], [status] FROM dbo.Controls WHERE id = @id", 
               command_type="Text",
               parameters="@id={id}",
               connection_string_setting="SqlConnectionString")
def get_value_function(req: func.HttpRequest, control: func.SqlRowList) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request to get value.')

    record_id = req.params.get('id')
    if not record_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            record_id = req_body.get('id')

    if record_id is None:
        return func.HttpResponse(
            "Por favor, proporciona 'id' en la URL usando ?id=<id>.",
            status_code=400
        )

    rows = list(map(lambda r: json.loads(r.to_json()), control))
    if not rows:
        return func.HttpResponse(
            f"No se encontró un registro con el id {record_id}.",
            status_code=404
        )

    return func.HttpResponse(
        json.dumps(rows),
        status_code=200,
        mimetype="application/json"
    )