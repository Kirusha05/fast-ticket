/** Convert 0-based row index to a spreadsheet-style label (0→A, 25→Z, 26→AA, …). */
export function rowLabel(r: number): string {
  let s = "";
  let n = r + 1;
  while (n > 0) {
    const mod = (n - 1) % 26;
    s = String.fromCharCode(65 + mod) + s;
    n = Math.floor((n - 1) / 26);
  }
  return s;
}

/** Create a full seat number like "A1", "B12", "AA3" from 0-based row/col. */
export function seatNumber(r: number, c: number): string {
  return `${rowLabel(r)}${c + 1}`;
}