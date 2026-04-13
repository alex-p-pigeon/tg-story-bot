import yookassa
from yookassa import Payment
import uuid
import fpgDB as pgDB

from config_reader import config #SECRET_KEY, ACCOUNT_ID

import logging
logger = logging.getLogger(__name__)

yookassa.Configuration.account_id = config.YC_ACCOUNT_ID.get_secret_value()      #ACCOUNT_ID
yookassa.Configuration.secret_key = config.YC_SECRET_KEY.get_secret_value()         #SECRET_KEY


PRICE_M = '499'
PRICE_MD = '499'
PRICE_Q = '2599'
PRICE_QD = '1299'
#PRICE_TM = '199.00'
#PRICE_TQ = '175.00'

# Цены без скидки
PRICE_Y = '5988'   # годовая обычная
PRICE_M = '999'    # месячная обычная
PRICE_W = '149'    # недельная

# Цены со скидкой 50%
PRICE_YD = '2990'  # годовая со скидкой
PRICE_MD = '499'   # месячная со скидкой


def fCreate():
    id_key = str(uuid.uuid4())
    res = Payment.create(
        {
            "amount": {
                "value": 1000,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/qartuliena_test_bot"
            },
            "capture": True,
            "description": "Заказ №72",
            "metadata": {
                'orderNumber': '72'
            },
            "receipt": {
                "customer": {
                    "full_name": "Ivanov Ivan Ivanovich",
                    "email": "email@email.ru",
                    "phone": "79211234567",
                    "inn": "6321341814"
                },
                "items": [
                    {
                        "description": "Переносное зарядное устройство Хувей",
                        "quantity": "1.00",
                        "amount": {
                            "value": 1000,
                            "currency": "RUB"
                        },
                        "vat_code": "2",
                        "payment_mode": "full_payment",
                        "payment_subject": "commodity",
                        "country_of_origin_code": "CN",
                        "product_code": "44 4D 01 00 21 FA 41 00 23 05 41 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 12 00 AB 00",
                        "customs_declaration_number": "10714040/140917/0090376",
                        "excise": "20.00",
                        "supplier": {
                            "name": "string",
                            "phone": "string",
                            "inn": "string"
                        }
                    },
                ]
            }
        }, id_key
    )

    return res.confirmation.confirmation_url, res.id




async def fCreatePayment(amount, chat_id, bAuto, pool, period, item_desc):
    id_key = str(uuid.uuid4())
    str_url = config.BOT_NAME.get_secret_value()


    isAutoPayment = True       #auto  ajarm
    if period == 'token': isAutoPayment = False

    var_query = (
        f"SELECT c_email, c_card_id FROM t_user WHERE c_user_id = '{chat_id}'"
    )
    var_Arr = await pgDB.fExec_SelectQuery(pool, var_query)
    email = str(var_Arr[0][0])
    #tel = str(var_Arr[0][1])
    str_payment_method_id = str(var_Arr[0][1])


    if len(email) > 0: dic_customer = {"email": email}

    amount_formatted = f"{amount}.00"
    dic_Amount = {'value': amount_formatted, 'currency': "RUB"}
    dic_payment_method_data = {'type': 'bank_card'}
    #if 1==1:
    dic_confirmation = {'type': 'redirect', 'return_url': str_url }         #'https://t.me/SpeakPalAI_bot'
    #else:
    #    dic_confirmation = {'type': 'redirect', 'return_url': 'https://t.me/qartuliena_test_bot'}
    dic_metadata = {'chat_id': chat_id, 'period': period}
    dic_receipt = {
        "customer": dic_customer,
        "items": [
            {
                "description": item_desc,
                "quantity": "1.00",
                "amount": dic_Amount,
                "vat_code": "1",
                "payment_mode": "full_payment",
                "payment_subject": "service"
            }
        ]
    }

    if bAuto:
        payment = Payment.create({
            "amount": dic_Amount,
            'payment_method_id': str_payment_method_id,
            'capture': True,
            'metadata': dic_metadata,
            'description': item_desc,
            "receipt": dic_receipt
        }, id_key)
    else:
        payment = Payment.create(
            {
                "amount": dic_Amount,
                "confirmation": dic_confirmation,
                'payment_method_data': dic_payment_method_data,
                'save_payment_method': isAutoPayment,
                "capture": True,
                "description": item_desc,
                "metadata": dic_metadata,
                "receipt": dic_receipt
            }, id_key
        )

    if bAuto:
        return None, payment.id
    else:
        return payment.confirmation.confirmation_url, payment.id

def fCheck(payment_id):
    payment= yookassa.Payment.find_one(payment_id)
    vAmount = 0
    if not payment.amount == None:
        vAmount = payment.amount.value
    vSaved = None
    vCardID = None
    if not payment.payment_method == None:
        if payment.payment_method.type == 'bank_card':
            vSaved = payment.payment_method.saved
            vCardID = payment.payment_method.id

    if payment.status == 'succeeded':
        return payment.status, payment.paid, vSaved, vCardID, vAmount, payment.metadata
    else:
        return payment.status, payment.paid, vSaved, vCardID, vAmount, payment.metadata


