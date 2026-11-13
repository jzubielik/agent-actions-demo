// Amounts arrive as integers in the minor unit of their currency and are never turned into a
// binary float: the formatter gets the exact decimal as a string.

function digitsOf(currency: string): number {
  return new Intl.NumberFormat("en", { style: "currency", currency }).resolvedOptions().maximumFractionDigits ?? 2;
}

export function decimalOf(minor: number, currency: string): `${number}` {
  if (!Number.isSafeInteger(minor)) throw new RangeError(`not a whole amount in minor units: ${minor}`);
  const digits = digitsOf(currency);
  const sign = minor < 0 ? "-" : "";
  const text = String(Math.abs(minor)).padStart(digits + 1, "0");
  const whole = text.slice(0, text.length - digits);
  return `${sign}${whole}${digits > 0 ? `.${text.slice(-digits)}` : ""}` as `${number}`;
}

export function formatMinor(minor: number, currency: string, locale: string): string {
  return new Intl.NumberFormat(locale, { style: "currency", currency }).format(decimalOf(minor, currency));
}
