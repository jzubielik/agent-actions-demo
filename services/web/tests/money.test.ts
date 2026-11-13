import { expect, test } from "vitest";
import { decimalOf, formatMinor } from "../src/money";

test("minor units become an exact decimal of the currency", () => {
  expect(decimalOf(1250, "EUR")).toBe("12.50");
  expect(decimalOf(5, "EUR")).toBe("0.05");
  expect(decimalOf(-310, "EUR")).toBe("-3.10");
  expect(decimalOf(1500, "JPY")).toBe("1500");
  expect(decimalOf(1250, "KWD")).toBe("1.250");
});

test("an amount that is not whole is refused", () => {
  expect(() => decimalOf(12.5, "EUR")).toThrow(RangeError);
});

test("an amount is formatted for the locale", () => {
  expect(formatMinor(123456, "EUR", "en-IE")).toBe("€1,234.56");
  expect(formatMinor(1500, "JPY", "en-US")).toBe("¥1,500");
});

test("a large amount keeps its last digit", () => {
  // 90071992547409.91 has no exact binary float; the formatter must still show every digit.
  expect(formatMinor(9007199254740991, "USD", "en-US")).toBe("$90,071,992,547,409.91");
});
