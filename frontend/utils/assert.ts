
export function asserFalsy <Val>(value: Val, message: string = ''): asserts value is NonNullable<Val> {
  if (!value) {
    throw new Error(message);
  }
}
