declare global {
  interface Window {
    console: Console
  }
}

export type ItemDefinition = {
  pk: number,
  name: string,
  group: {
    title: string
  }[]
}

export type CatalogEntry = {
  pk: number,
  item_definition: ItemDefinition,
  to_buy: boolean,
  catalog_group: number
}

export type ApiResult<Item> = {
  count: number,
  next: string | null,
  previous: string | null,
  results: Item[]
}
