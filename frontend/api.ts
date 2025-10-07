import { ApiResult, CatalogItem } from "./const";
import { COOKIE_ERROR } from "./utils/assert";
import { memo } from "./utils/memo";

const API_URL = '/catalog/api';
const TOKEN_NAME = "csrftoken";

export const getCsrfToken = memo((ctx: Window): string => {
  const keyVals = ctx.document.cookie.split(';');
  for (const keyVal of keyVals) {
    const [key, val] = keyVal.split('=');
    if (key.trim() === TOKEN_NAME) {
      return val.trim();
    }
  }
  throw new Error(COOKIE_ERROR);
});

export const searchApi = async (query: string): Promise<ApiResult<CatalogItem>> => {
  return fetch(`${API_URL}/catalog-resources/?search=${query}`)
    .then(response => response.json())
};

export const buyApi = async (ctx: Window, pk: number, toBuy: boolean): Promise<CatalogItem> => {
  return fetch(`${API_URL}/catalog-resources/${pk}/`, {
    method: 'PATCH',
    headers: {
      'X-CSRFToken': getCsrfToken(ctx),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ to_buy: toBuy })
  })
  .then(response => response.json())
};

