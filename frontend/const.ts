declare global {
  interface Window {
    console: Console
  }
}

export type CatalogGroup = {
  title: string,
}

export type CatalogResource = {
  pk: number,
  group: CatalogGroup[],
  name: string,
  to_buy: boolean,
}
export type ApiResult<Item> = {
  count: number,
  next: string | null,
  previous: string | null,
  results: Item[]
}
