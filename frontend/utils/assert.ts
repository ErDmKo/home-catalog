export const DOM_ERROR = 'd';
export const INTERNAL_ERROR = 'i';
export const COOKIE_ERROR = 'c';
export const TYPE_ERROR = 't';

export function asserFalsy <Val>(value: Val, message: string = ''): asserts value is NonNullable<Val> {
  if (!value || Number.isNaN(value)) {
    throw new Error(message);
  }
}

export function assertType<T>(
  value: unknown,
  constructor: new (...args: any[]) => T
): asserts value is T {
  if (!(value instanceof constructor)) {
    throw new Error(TYPE_ERROR);
  }
}
