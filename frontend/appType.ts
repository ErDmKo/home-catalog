declare global {
  interface Window {
    console: Console
  }
}

export type CatalogItem = {
  pk: number,
  name: string
  to_buy : boolean
  group: {
    title: string
  }[]
}

export type ApiResult<Item> = {
  count: number,
  next: string | null,
  previous: string | null,
  results: Item[]
}
