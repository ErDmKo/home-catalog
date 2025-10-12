import { cleanHtml, domCreator, genAttr, genClass, genProp, genTagDiv, genText } from "../utils/dom";
import { next, observer, subscribe } from "../utils/observer";
import type { ObserverInstance } from "../utils/observer";
import { asserFalsy, DOM_ERROR } from "../utils/assert";
import type { SelectOption } from "./select";

export const RENDER = 0;
export const UPDATE = 1;

export const NOT_BUY = 0;
export const TO_BUY = 1;
export const ADD_GROUP = 2;
export const ADD_ITEM = 3;

export type ItemActions = 
  | [typeof NOT_BUY, value: string] 
  | [typeof TO_BUY, value: string]
  | [typeof ADD_ITEM, value: string]
  | [typeof ADD_GROUP, value: string];

export type DropdownAction =
  | [typeof RENDER, SelectOption[], inputValue: string]
  | [typeof UPDATE, SelectOption[]];

const FONT_SIZE_NORMAL = '16px';
const FONT_SIZE_SMALL = '12px';

const optionStyle = () => ({
  fontSize: FONT_SIZE_NORMAL,
  padding: '10px',
  cursor: 'pointer',
  borderTop: '1px solid #ccc'
});

const optionActionStyle = (option: SelectOption) => ({
  display: 'inline-block',
  fontSize: FONT_SIZE_SMALL,
  color: option.to_buy ? 'red' : 'green', 
  padding: '5px 0px',
});

const creationActionStyle = {
  fontSize: FONT_SIZE_SMALL,
  display: 'inline-block',
  padding: '10px 15px'
};

const optionTemplate = (option: SelectOption, actionObserver: ObserverInstance<ItemActions>) => {
  return genTagDiv([
    genAttr('data-id', option.value),
    genProp('style', optionStyle())], [
    genTagDiv([
      genText(option.label),
    ]),
    genTagDiv([
      genText(option.to_buy ? '🔴 Нужно купить' : '🟢 Покупать не нужно'),
      genProp('onclick', () => {
        actionObserver(next([option.to_buy ? NOT_BUY : TO_BUY, option.value]));
      }),
      genProp('style', optionActionStyle(option))
    ])
  ])
};

const renderOptions = (
  ctx: Window,
  root: Element,
  options: SelectOption[],
  actionObserver: ObserverInstance<ItemActions>,
  inputValue: string
) => {
  const optionList = options.map((option) => optionTemplate(option, actionObserver));
  let content = optionList;

  if (!(options.length && !options.find(option => option.label !== inputValue))) {
    content = [genTagDiv([genProp('style', optionStyle())], [
        genTagDiv([
          genText(`Добавить новую вещь: "${inputValue}"`),
          genProp('style', creationActionStyle),
          genProp('onclick', () => {
            actionObserver(next([ADD_ITEM, inputValue]));
          }),
        ])
      ])].concat(optionList);
  }
  const optionsTemplate = genTagDiv([genClass('options')], content);
  cleanHtml(root);
  if (inputValue) {
    domCreator(ctx, root, optionsTemplate);
  }
};

const updateOptions = (
  ctx: Window, 
  root: Element,
  data: SelectOption[],
  actionObserver: ObserverInstance<ItemActions>
) => {
  const options = data.reduce((e, option) => {
    e[option.value] = option;
    return e;
  }, {} as Record<string, SelectOption | undefined>);
  const [optionsRoot] = root.children;
  asserFalsy(optionsRoot, DOM_ERROR);
  for (const elem of optionsRoot.children) {
    const value = elem.getAttribute('data-id');
    const option = options[`${value}`];
    if (option) {
      const template = optionTemplate(option, actionObserver);
      const wrappper = ctx.document.createElement('div');
      domCreator(ctx, wrappper, template);
      const [newElem] = wrappper.children;
      optionsRoot.replaceChild(newElem, elem);
    }
  }
}

export const makeOptionsDropdown = (
  ctx: Window,
  container: HTMLElement
): [ObserverInstance<DropdownAction>, ObserverInstance<ItemActions>] => {
  const dropdownObserver = observer<DropdownAction>();
  const actionObserver = observer<ItemActions>();
  
  dropdownObserver(subscribe((action) => {
    const [type, ...args] = action;
    if (type === RENDER) {
      const [options, inputValue] = args as [SelectOption[], string];
      renderOptions(ctx, container, options, actionObserver, inputValue);
    } else if (type === UPDATE) {
      const [options] = args as [SelectOption[]];
      updateOptions(ctx, container, options, actionObserver);
    }
  }));
  
  return [dropdownObserver, actionObserver];
};
