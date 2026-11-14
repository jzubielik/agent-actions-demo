// The rows of the order history page: one per order, newest first as the API returns them.
import { formatMinor } from "./money";

export interface HistoryRow {
  id: string;
  badge: string;
  total: string;
  placed: string;
}

// The colour of the status badge.
const BADGES: Record<string, string> = {
  draft: "grey",
  placed: "amber",
  paid: "green",
};

export function historyRows(orders: any[], locale: string): HistoryRow[] {
  return orders.map((order) => ({
    id: order.id,
    badge: BADGES[order.status] as string,
    total: formatMinor(order.total_minor, order.currency, locale),
    placed: new Intl.DateTimeFormat(locale, { dateStyle: "medium", timeZone: "UTC" }).format(new Date(order.created_at)),
  }));
}
