from fastapi import APIRouter, HTTPException, Depends
from app.schemas.pago_schema import PagoCreate
from app.controllers.pago_controller import PagoController
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/api/v1/pagos", tags=["Pagos"])
pago_ctrl = PagoController()

@router.post("/", status_code=201)
def registrar_abono(pago: PagoCreate, current_user: Usuario = Depends(get_current_user)):
    # Se inyecta el current_user.id directamente desde el validador del token
    exito = pago_ctrl.registrar_pago(credito_id=pago.credito_id, usuario_id=current_user.id, monto=pago.monto)
    if not exito: raise HTTPException(status_code=400, detail="Error transaccional al procesar el abono.")
    return {"mensaje": "Abono registrado correctamente"}