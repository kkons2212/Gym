"""Repository operations for invoices."""

from __future__ import annotations

from typing import List, Optional, Type

from mysql.connector.cursor import MySQLCursor

from models.invoice import Invoice
from repositories.base_repository import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    """Read and write invoices."""

    table_name = "Invoice"
    id_column = "InvoiceId"
    _select_query = (
        "SELECT `Invoice`.*, "
        "`Invoice`.`CheckInLogCheckInId` AS `check_in_log_id` "
        "FROM `Invoice`"
    )

    @property
    def entity_type(self) -> Type[Invoice]:
        return Invoice

    def create_with_cursor(
        self, cursor: MySQLCursor, invoice: Invoice
    ) -> None:
        """Insert an invoice using the caller's transaction."""
        query = (
            "INSERT INTO `Invoice` "
            "(`InvoiceId`, `InvoiceCode`, `TransactionType`, "
            "`SubtotalAmount`, "
            "`TotalAmount`, `PaymentMethod`, `Status`, `RefundAmount`, "
            "`RefundReason`, `paid_at`, `UserName`, `SubscriptionId`, "
            "`CreatedByAdminId`, `CheckInLogCheckInId`) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        params = (
            invoice.invoice_id,
            invoice.invoice_code,
            invoice.transaction_type,
            invoice.subtotal_amount,
            invoice.total_amount,
            invoice.payment_method,
            invoice.status,
            invoice.refund_amount,
            invoice.refund_reason,
            invoice.paid_at,
            invoice.username,
            invoice.subscription_id,
            invoice.created_by_admin_id,
            invoice.check_in_log_id,
        )
        self.execute_with_cursor(cursor, query, params)

    def get_by_id(self, record_id: str) -> Optional[Invoice]:
        """Fetch an invoice and map its physical check-in foreign key."""
        rows = self.execute_query(
            f"{self._select_query} WHERE `InvoiceId` = %s LIMIT 1",
            (record_id,),
        )
        return Invoice.from_row(rows[0]) if rows else None

    def get_all(self) -> List[Invoice]:
        """Fetch invoices and map their physical check-in foreign keys."""
        rows = self.execute_query(self._select_query)
        return [Invoice.from_row(row) for row in rows]

    def get_recent_invoices(self, limit: int = 50) -> List[Invoice]:
        """Fetch the newest invoices first."""
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit phải là số nguyên dương.")

        rows = self.execute_query(
            f"{self._select_query} "
            "ORDER BY `paid_at` DESC, `InvoiceId` DESC LIMIT %s",
            (limit,),
        )
        return [Invoice.from_row(row) for row in rows]
