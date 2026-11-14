// What the order page shows, worked out from an order of the API.
import type { Order, Status } from "./client";
import { formatMinor } from "./money";

export interface SummaryLine {
  label: string;
  amount: string;
}

export interface OrderSummary {
  status: string;
  lines: SummaryLine[];
  subtotal: string;
  // Absent when the order has no discount, so the page shows no empty row.
  discount?: string;
  total: string;
  placed: string;
  canPlace: boolean;
  // A paid order is refunded, not cancelled, so the page offers no cancel button for it.
  canCancel: boolean;
}

const STATUS_LABELS: Record<Status, string> = {
  draft: "Draft",
  placed: "Waiting for payment",
  paid: "Paid",
  cancelled: "Cancelled",
};

export function summarize(order: Order, locale: string): OrderSummary {
  const money = (minor: number) => formatMinor(minor, order.currency, locale);
  const summary: OrderSummary = {
    status: STATUS_LABELS[order.status],
    lines: order.items.map((item) => ({
      label: item.quantity === 1 ? item.sku : `${item.quantity} × ${item.sku}`,
      amount: money(item.quantity * item.unit_price_minor),
    })),
    subtotal: money(order.subtotal_minor),
    total: money(order.total_minor),
    placed: new Intl.DateTimeFormat(locale, { dateStyle: "medium", timeZone: "UTC" }).format(new Date(order.created_at)),
    canPlace: order.status === "draft",
    canCancel: order.status === "draft" || order.status === "placed",
  };
  if (order.discount_minor > 0) summary.discount = money(-order.discount_minor);
  return summary;
}
