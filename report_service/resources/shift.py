from db import db
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import MessageOnlySchema, ShiftOpenSchema, ShiftSchema

blp = Blueprint("Shift", "shift", description="Operations on shifts")


@blp.route("/shop/<int:shop_id>/shift")
class Shift(MethodView):
    @blp.response(200, ShiftSchema, description="Shift found and returned successfully.")
    @blp.alt_response(400, description="There are more then 1 shift opened now.")
    @blp.alt_response(404, description="Opened shifts not found")
    def get(self, shop_id):
        # Get current shift
        opened_shifts = list(db.db.shifts.find({"shop_id": shop_id, "status": "opened"}))
        if not opened_shifts or len(opened_shifts) == 0:
            abort(404, message="No shifts are opened")
        if len(opened_shifts) > 1:
            abort(400, message="There shouldn't be more then 1 shifts opened at once")
        
        return opened_shifts[0]

    @blp.arguments(ShiftOpenSchema)
    @blp.response(201, MessageOnlySchema, description="Shift opened successfully.")
    @blp.alt_response(409, description="There is already a shift in the shop.")
    def post(self, shift_open_data, shop_id):
        opened_shifts = db.db.shifts.find({"shop_id": shop_id, "status": "opened"})
        if opened_shifts and len(list(opened_shifts)) > 0:
            abort(409, message="There is already shift opened.")

        db.db.shifts.insert_one({"shop_id": shop_id, 
                                 "status": "opened", 
                                 **shift_open_data})
        
        return {"message": "Shift opened successfully."}


# @blp.route("/shop/<int:shop_id>/shift/close")
# class ShiftClose(MethodView):
#     @blp.arguments(ShiftCloseSchema)
#     @blp.arguments(UserCheckSchema, location='query')
#     @blp.response(200, MessageOnlySchema, description="Shift closed successfully.")
#     @blp.alt_response(400, description="There are more then 1 shift opened now.")
#     @blp.alt_response(401, description="The same person should open and close the shift.")
#     @blp.alt_response(404, description="Opened shifts not found")
#     def post(self, shift_close_data, user_check_data, shop_id):
#         opened_shifts = db.db.shifts.find({"shop_id": shop_id, "status": "opened"})
#         if not opened_shifts or len(opened_shifts) == 0:
#             abort(404, message="No shifts are opened")
#         if len(opened_shifts) > 1:
#             abort(400, message="There shouldn't be more then 1 shifts opened at once")
#         shift = opened_shifts[0]
#         if shift["user_id"] != user_check_data["user_id"]:
#             abort(401, "Should be the person who opened the shift to close it")
#         shift["status"] = "closed"
#         shift["close_time"] = shift_close_data["close_time"]
#         db.db.shifts.update_one({"shop_id": shop_id, "status": "opened"}, shift)
#         return{"message": "Shift closed successfully."}
