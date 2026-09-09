# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from zeep.helpers import serialize_object

from odoo.addons.liza_base.liza_const import (
    SERVICE_INTEGRATOR_ID,
    SERVICE_INTEGRATOR_SECRET,
)
from odoo.addons.liza_base.liza_utils import _liza_create_hash, liza_client


def liza_send_open_invoices(
    url,
    login,
    password,
    lang,
    package_version,
    supplier_country,
    supplier_identifier_type,
    supplier_identifier,
    invoices_list,
):
    """
    Send open invoices to Liza AutoPayex API (v4.0).
    Returns the serialized response dict.
    """
    client = liza_client(url, "liza_payment_info")
    response = client.service.SendOpenInvoices(
        request=dict(
            Login=login,
            Password=password,
            ServiceIntegrator=SERVICE_INTEGRATOR_ID,
            LoginHash=_liza_create_hash(login, password, SERVICE_INTEGRATOR_SECRET),
            Language=lang,
            PackageVersion=package_version,
            SupplierCountry=supplier_country,
            SupplierIdentifierType=supplier_identifier_type,
            SupplierIdentifier=supplier_identifier,
            InvoicesList={"InvoiceRequest": invoices_list},
        )
    )
    res_dict = serialize_object(response)
    status = res_dict.get("StatusCode", -1)
    if status != 0:
        return status, res_dict.get("StatusMessage", "")
    return status, res_dict.get("InvoicesSummary", {})
