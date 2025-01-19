export const DOM_ERROR = '';
export const INTERNAL_ERROR = '';
export const COOKIE_ERROR = '';

export function asserFalsy <Val>(value: Val, message: string = ''): asserts value is NonNullable<Val> {
  if (!value || Number.isNaN(value)) {
    throw new Error(message);
  }
}
