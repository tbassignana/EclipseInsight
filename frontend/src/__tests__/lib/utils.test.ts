import { cn, formatDate, formatNumber, isValidUrl, copyToClipboard } from "@/lib/utils";

describe("cn utility", () => {
  it("merges class names", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("handles conditional classes", () => {
    expect(cn("foo", false && "bar", "baz")).toBe("foo baz");
  });

  it("handles tailwind merge conflicts", () => {
    expect(cn("p-4", "p-2")).toBe("p-2");
    expect(cn("text-red-500", "text-blue-500")).toBe("text-blue-500");
  });
});

describe("formatDate utility", () => {
  it("formats recent dates as relative time", () => {
    const now = new Date();
    const result = formatDate(now.toISOString());
    expect(result).toMatch(/just now|seconds? ago|minutes? ago/);
  });

  it("formats older dates with actual date", () => {
    const oldDate = new Date("2023-01-15T12:00:00Z");
    const result = formatDate(oldDate.toISOString());
    expect(result).toMatch(/Jan|2023/);
  });
});

describe("formatNumber utility", () => {
  it("formats small numbers without abbreviation", () => {
    expect(formatNumber(500)).toBe("500");
    expect(formatNumber(999)).toBe("999");
  });

  it("formats thousands with K suffix", () => {
    expect(formatNumber(1000)).toBe("1K");
    expect(formatNumber(1500)).toBe("1.5K");
    expect(formatNumber(10000)).toBe("10K");
  });

  it("formats millions with M suffix", () => {
    expect(formatNumber(1000000)).toBe("1M");
    expect(formatNumber(2500000)).toBe("2.5M");
  });
});

describe("isValidUrl utility", () => {
  it("returns true for valid HTTP URLs", () => {
    expect(isValidUrl("http://example.com")).toBe(true);
    expect(isValidUrl("https://example.com")).toBe(true);
    expect(isValidUrl("https://example.com/path?query=1")).toBe(true);
  });

  it("returns false for invalid URLs", () => {
    expect(isValidUrl("not-a-url")).toBe(false);
    expect(isValidUrl("ftp://example.com")).toBe(false);
    expect(isValidUrl("")).toBe(false);
  });
});

describe("copyToClipboard utility", () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn().mockResolvedValue(undefined),
      },
    });
  });

  it("copies text to clipboard", async () => {
    await copyToClipboard("test text");
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("test text");
  });
});
