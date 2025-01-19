import { asserFalsy, DOM_ERROR } from "../utils/assert";
import { bindArg } from "../utils/bind";
import { cleanHtml, domCreator, genAttr, genClass, genProp, genRef, genTagDiv, genText } from "../utils/dom";
import { delayOperator, lazyObserver, next, observer, ObserverInstance, subscribe } from "../utils/observer";

export type SelectOption = {
  label: string,
  value: string,
  to_buy: boolean,
}

export const OPTIONS_ADD = 0;
export const OPTIONS_UPDATE = 1;

export type OptionsAction =
  | [typeof OPTIONS_ADD, SelectOption[]]
  | [typeof OPTIONS_UPDATE, SelectOption[]]

export const PATH_NOT_BUY = 0;
export const PATH_TO_BUY = 1;

type ItemActions = 
  | [typeof PATH_NOT_BUY, value: string] 
  | [typeof PATH_TO_BUY, value: string];

const FONT_SIZE = '16px';


const wrapperElem = (ctx: Window, element: Element): HTMLDivElement => {
  asserFalsy(element.parentElement, DOM_ERROR);
  const wrapperTemplate = genTagDiv([
    genClass('wrapper'),
    genProp('style', {
      border: '1px solid #ccc',
      fontSize: FONT_SIZE,
      margin: '20px 0',
    }),
    genRef()
  ], [
    genTagDiv([genClass('options'), genRef()], [])
  ]);

  const [wrapperRef, optionsRef] = domCreator(ctx, element.parentElement, wrapperTemplate);
  wrapperRef.prepend(element);

  if (!(optionsRef instanceof HTMLDivElement)) {
    throw new Error(DOM_ERROR);
  }
  if (!(element instanceof HTMLInputElement)) {
    throw new Error(DOM_ERROR);
  }
  Object.assign(element.style, {
    boxSizing: 'border-box',
    fontSize: FONT_SIZE,
    width: '100%',
    padding: '10px',
    border: 'none',
    outline: 'none'
  });
  return optionsRef;
}

const optionTemplate = (option: SelectOption, actionObserver: ObserverInstance<ItemActions>) => {
  return genTagDiv([
    genAttr('data-id', option.value),
    genProp('style', {
      fontSize: FONT_SIZE,
      padding: '10px',
      cursor: 'pointer',
      borderTop: '1px solid #ccc'
  })], [
    genTagDiv([
      genText(option.label),
    ]),
    genTagDiv([
      genText(option.to_buy ? '🔴 Нужно купить' : '🟢 Покупать не нужно'),
      genProp('onclick', () => {
        actionObserver(next([option.to_buy ? PATH_NOT_BUY : PATH_TO_BUY, option.value]));
      }),
      genProp('style', {
        display: 'inline-block',
        fontSize: '12px',
        color: option.to_buy ? 'red' : 'green', 
        padding: '5px 0px',
        margin: '10px 0px 0px'
      })
    ])
  ])
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

const renderOptions = (
  ctx: Window,
  root: Element,
  options: SelectOption[],
  actionObserver: ObserverInstance<ItemActions>
) => {
  const optionsTemplate = genTagDiv(
    [genClass('options')], 
    options.map((option) => optionTemplate(option, actionObserver))
  );

  cleanHtml(root);
  if (options.length) {
    domCreator(ctx, root, optionsTemplate);
  }
};

export const initSelect = (
  ctx: Window,
  input: HTMLInputElement, 
  label: Element
): [ObserverInstance<string>, ObserverInstance<OptionsAction>, ObserverInstance<ItemActions>]  => {
  const optionsRef = wrapperElem(ctx, input);
  const inputObserver = observer<string>();
  const dataObserver = observer<OptionsAction>();
  const actionObserver = observer<ItemActions>();
  const [cancelSet, cancelGet] = lazyObserver<boolean>();

  label.addEventListener('input', (e) => {
    if (!(e.target instanceof HTMLInputElement)) {
      return;
    }
    const nextValue = e.target.value;
    if (nextValue) {
      cancelSet(false);
      inputObserver(next(nextValue));
    } else {
      cancelSet(true);
    }
  });

  let isCanceled: boolean = false;

  cancelGet((newIsCanceled) => {
    isCanceled = newIsCanceled;
    if (isCanceled) {
      renderOptions(ctx, optionsRef, [], actionObserver);
    }
  });

  dataObserver(subscribe((action) => {
    const [type, data] = action;
    if (type === OPTIONS_ADD) {
      renderOptions(ctx, optionsRef, isCanceled ? [] : data, actionObserver);
    } else if (type === OPTIONS_UPDATE) {
      updateOptions(ctx, optionsRef, data, actionObserver);
    }
  }));

  return [
    inputObserver(bindArg(500, delayOperator)),
    dataObserver,
    actionObserver
  ];
}

