export type Brand<T, B extends string> = T & { readonly __brand: B };

export function brand<T extends string, B extends string>(value: T): Brand<T, B> {
  return value as Brand<T, B>;
}

export function isNonEmptyString(value: string): boolean {
  return value.trim().length > 0;
}
