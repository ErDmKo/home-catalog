import { asserFalsy } from "./utils/assert";
import { bindArg } from "./utils/bind";
import { cleanHtml, domCreator, genClass, genRef, genTagDiv, genText } from "./utils/dom";
import { delayOperator, next, observer, subscribe } from "./utils/observer";

declare global {
  interface Window {
    console: Console
  }
}

type CatalogItem = {
  name: string
  group: {
    title: string
  }[]
}

type ApiResult<Item> = {
  count: number,
  next: string | null,
  previous: string | null,
  results: Item[]
}
const API_URL = '/catalog/api';

const DOM_ERROR =  'd';

const searchApi = async (query: string): Promise<ApiResult<CatalogItem>> => {
  return fetch(`${API_URL}/items?search=${query}`)
    .then(response => response.json())
}

const wrapperElem = (ctx: Window, element: Element): HTMLDivElement => {
  asserFalsy(element.parentElement, DOM_ERROR);
  const wrapperTemplate = genTagDiv([
    genClass('wrapper'),
    genRef()
  ], [
    genTagDiv([genClass('options'), genRef()], [])
  ]);

  const [wrapperRef, optionsRef] = domCreator(ctx, element.parentElement, wrapperTemplate);
  wrapperRef.prepend(element);

  if (!(optionsRef instanceof HTMLDivElement)) {
    throw new Error(DOM_ERROR);
  }
  return optionsRef;
}

const renderOptions = (ctx: Window, root: Element, options: CatalogItem[]) => {
  const optionsTemplate = genTagDiv([genClass('options')], options.map((option) => {
    const goupFullName = option.group.length ? `${option.group.map(e => e.title).join(", ")}: ` : '';
    const optionName = `${goupFullName}${option.name}`;
    return genTagDiv([], [
      genTagDiv([genText(optionName)]),
    ])
  }));
  cleanHtml(root);
  domCreator(ctx, root, optionsTemplate);
}

export const intSelect = (ctx: Window, selector: string) => {
  const select = document.querySelector(selector);
  asserFalsy(select, DOM_ERROR);
  const input = select.querySelector('input');
  asserFalsy(input, DOM_ERROR);

  const optionsRef = wrapperElem(ctx, input);

  const inputObserver = observer<string>();

  select.addEventListener('input', (e) => {
    if (!(e.target instanceof HTMLInputElement)) {
      return;
    }
    const nextValue = e.target.value;
    if (nextValue) {
      inputObserver(next(nextValue));
    }
  })

  const fetchObserver = inputObserver(bindArg(500, delayOperator));

  fetchObserver(subscribe((value: string) => {
    searchApi(value)
      .then((data) => {
        renderOptions(ctx, optionsRef, data.results);
      });
  }));
}
