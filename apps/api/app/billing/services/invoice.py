"""Invoice and payment service."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.billing import Customer, Invoice, Payment
from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self) -> None:
        super().__init__(Invoice)

    async def list_for_customer(
        self,
        db: AsyncSession,
        customer_id: uuid.UUID,
    ) -> list[Invoice]:
        stmt = (
            select(Invoice)
            .where(Invoice.customer_id == customer_id)
            .order_by(desc(Invoice.created_at))
        )
        result = await db.execute(stmt)
        return result.scalars().all()


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self) -> None:
        super().__init__(Payment)


invoice_repository = InvoiceRepository()
payment_repository = PaymentRepository()


class InvoiceService:
    async def list_for_user(
        self,
        db: AsyncSession,
        customer: Customer,
    ) -> list[Invoice]:
        return await invoice_repository.list_for_customer(db, customer.id)

    async def from_webhook(
        self,
        db: AsyncSession,
        customer: Customer,
        data: dict,
    ) -> Invoice:
        invoice = Invoice(
            customer_id=customer.id,
            provider=customer.provider,
            provider_invoice_id=data.get("id"),
            number=data.get("number"),
            status=data.get("status", "draft"),
            currency=data.get("currency", "usd"),
            subtotal=Decimal(str(data.get("subtotal", 0))),
            tax=Decimal(str(data.get("tax", 0))),
            total=Decimal(str(data.get("total", 0))),
            paid=Decimal(str(data.get("amount_paid", 0))),
            pdf_url=data.get("hosted_invoice_url"),
            metadata=data,
        )
        return await invoice_repository.create(db, invoice)

    async def get(
        self,
        db: AsyncSession,
        invoice_id: uuid.UUID,
    ) -> Invoice:
        invoice = await invoice_repository.get(db, invoice_id)
        if not invoice:
            raise NotFoundError("Invoice not found")
        return invoice


class PaymentService:
    async def from_webhook(
        self,
        db: AsyncSession,
        customer: Customer,
        data: dict,
    ) -> Payment:
        payment = Payment(
            customer_id=customer.id,
            provider=customer.provider,
            provider_payment_id=data.get("id"),
            amount=Decimal(str(data.get("amount", 0))),
            currency=data.get("currency", "usd"),
            status=data.get("status", "pending"),
            failure_message=data.get("failure_message"),
            metadata=data,
        )
        return await payment_repository.create(db, payment)


invoice_service = InvoiceService()
payment_service = PaymentService()
