import { ApiResult, CatalogItem } from "./const";
import { initSelect } from "./select/select";
import { asserFalsy } from "./utils/assert";
import { DOM_ERROR } from "./utils/dom";
import { next, subscribe } from "./utils/observer";

const API_URL = '/catalog/api';

const searchApi = async (query: string): Promise<ApiResult<CatalogItem>> => {
  return fetch(`${API_URL}/items/?search=${query}`)
    .then(response => response.json())
}

export const intSelect = (ctx: Window, selector: string) => {
  const label = document.querySelector(selector);
  asserFalsy(label, DOM_ERROR);
  const input = label.querySelector('input');
  asserFalsy(input, DOM_ERROR);

  const [inputObserver, dataObserver] = initSelect(ctx, input, label);

  inputObserver(subscribe((value: string) => {
    searchApi(value)
      .then((data) => {
        const selectOptions = data.results.map((option) => {
          const goupFullName = option.group.length ? `${option.group.map(e => e.title).join(", ")}: ` : '';
          const optionName = `${goupFullName}${option.name}`;
          return {
            label: optionName,
            value: option.pk,
            to_buy: option.to_buy
          }
        })
        dataObserver(next(selectOptions))
      });
  }));
}
