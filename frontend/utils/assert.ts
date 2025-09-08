export const DOM_ERROR = 'd';
export const INTERNAL_ERROR = 'i';
export const COOKIE_ERROR = 'c';

export function asserFalsy <Val>(value: Val, message: string = ''): asserts value is NonNullable<Val> {
  if (!value || Number.isNaN(value)) {
    throw new Error(message);
  }
}
