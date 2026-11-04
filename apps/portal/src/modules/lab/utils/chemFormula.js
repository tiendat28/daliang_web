const SUBSCRIPT_DIGITS = { '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉' }
const SUPERSCRIPT_CHARS = { '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '+': '⁺', '-': '⁻' }

// A real formula is made up only of element/formula characters - letters, digits,
// parentheses, a dot (hydrates), or +/- (charges). Anything else (spaces, Vietnamese
// diacritics, ...) means it's a product/brand name (e.g. "Nhuộm đen 415", "Orange 302")
// whose digits must NOT be touched.
const FORMULA_ONLY = /^[A-Za-z0-9().,+\-·]+$/

/**
 * Formats a chemical formula for display: stoichiometric numbers become
 * subscript (H2SO4 -> H₂SO₄), ionic charges become superscript (Zn2+ -> Zn²⁺).
 * Leaves non-formula text (product names, codes with spaces/diacritics) untouched.
 */
export function formatFormula(text) {
  if (!text) return text
  const str = String(text)
  if (!FORMULA_ONLY.test(str)) return str
  let result = str.replace(/(\d+)([+-])/g, (_, digits, sign) =>
    digits.split('').map(d => SUPERSCRIPT_CHARS[d]).join('') + SUPERSCRIPT_CHARS[sign]
  )
  result = result.replace(/\d+/g, m => m.split('').map(d => SUBSCRIPT_DIGITS[d]).join(''))
  return result
}
