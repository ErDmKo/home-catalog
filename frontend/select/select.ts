import { asserFalsy } from "../utils/assert";
import { bindArg } from "../utils/bind";
import { cleanHtml, DOM_ERROR, domCreator, genClass, genProp, genRef, genTagDiv, genText } from "../utils/dom";
import { delayOperator, lazyObserver, next, observer, ObserverInstance, subscribe } from "../utils/observer";

type SelectOption = {
  label: string,
  value: string,
  to_buy: boolean,
  pk: number
}

const TO_BUY_ACTION = 0;
const ADD_ACTION = 1;

type Actions = typeof TO_BUY_ACTION | typeof ADD_ACTION;

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

const renderOptions = (ctx: Window, root: Element, options: SelectOption[], actionObserver: ObserverInstance<Actions>) => {
  const optionsTemplate = genTagDiv([genClass('options')], options.map((option) => {
    return genTagDiv([
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
        genText(option.to_buy ? 'Купить' : 'Не купить'),
        genProp('onclick', () => {
          actionObserver(next(option.to_buy ? TO_BUY_ACTION : ADD_ACTION));
        }),
        genProp('style', { fontSize: '12px', color: '#ccc' })
      ])
    ])
  }));
  cleanHtml(root);
  if (options.length) {
    domCreator(ctx, root, optionsTemplate);
  }
};

export const initSelect = <Data extends SelectOption>(
  ctx: Window,
  input: HTMLInputElement, 
  label: Element
): [ObserverInstance<string>, ObserverInstance<Data[]>]  => {
  const optionsRef = wrapperElem(ctx, input);
  const inputObserver = observer<string>();
  const dataObserver = observer<Data[]>();
  const actionObserver = observer<Actions>();
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

  dataObserver(subscribe((newData) => {
    renderOptions(ctx, optionsRef, isCanceled ? [] : newData, actionObserver);
  }));

  return [
    inputObserver(bindArg(500, delayOperator)),
    dataObserver
  ];
}

