import { asserFalsy, assertType, DOM_ERROR } from "../utils/assert";
import { bindArg } from "../utils/bind";
import { domCreator, genClass, genProp, genRef, genTagDiv } from "../utils/dom";
import { delayOperator, lazyObserver, next, observer, ObserverInstance, subscribe } from "../utils/observer";
import { makeClearable } from "./clearable-input";
import { makeOptionsDropdown, RENDER, UPDATE, type ItemActions } from "./options-dropdown";

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

const FONT_SIZE_NORMAL = '16px';

const inputContainerStyle = {
  position: 'relative' as const  // Position for the clear button
};

const inputStyle = {
  boxSizing: 'border-box' as const,
  fontSize: FONT_SIZE_NORMAL,
  width: '100%',
  padding: '10px',
  paddingRight: '44px',
  border: 'none',
  outline: 'none'
};

const wrapperElem = (ctx: Window, element: Element): [HTMLDivElement, HTMLElement] => {
  asserFalsy(element.parentElement, DOM_ERROR);
  const wrapperTemplate = genTagDiv([
    genClass('wrapper'),
    genProp('style', {
      border: '1px solid #ccc',
      fontSize: FONT_SIZE_NORMAL,
      margin: '20px 0',
    })
  ], [
    genTagDiv([
      genClass('input-container'),
      genProp('style', inputContainerStyle),
      genRef()
    ], []),
    genTagDiv([genClass('options'), genRef()], [])
  ]);

    const [wrapperRef, optionsRef] = domCreator(ctx, element.parentElement, wrapperTemplate);
    wrapperRef.prepend(element);

    assertType(optionsRef, HTMLDivElement);
    assertType(element, HTMLInputElement);
    
    Object.assign(element.style, inputStyle);
    
    return [optionsRef, wrapperRef];
}

export const initSelect = (
  ctx: Window,
  input: HTMLInputElement, 
  label: Element
): [ObserverInstance<string>, ObserverInstance<OptionsAction>, ObserverInstance<ItemActions>]  => {
  const [optionsRef, wrapperRef] = wrapperElem(ctx, input);
  const inputObserver = observer<string>();
  const dataObserver = observer<OptionsAction>();
  const [dropdownObserver, dropdownActionObserver] = makeOptionsDropdown(ctx, optionsRef);
  const [cancelSet, cancelGet] = lazyObserver<boolean>();
  let inputValue = input.value;

  // Create internal observer for input value changes
  const inputValueWriteObserver = observer<string>();
  
  // Subscribe to handle value changes from any source
  inputValueWriteObserver(subscribe((nextValue) => {
    input.value = nextValue;
    inputValue = nextValue;
    
    if (nextValue) {
      cancelSet(false);
      inputObserver(next(nextValue));
    } else {
      cancelSet(true);
    }
  }));

  // Source 1: User typing
  label.addEventListener('input', (e) => {
    if (!(e.target instanceof HTMLInputElement)) {
      return;
    }
    inputValueWriteObserver(next(e.target.value));
  });

  // Source 2: Clear button
  makeClearable(ctx, wrapperRef, inputValueWriteObserver);

  let isCanceled: boolean = false;

  cancelGet((newIsCanceled) => {
    isCanceled = newIsCanceled;
    if (isCanceled) {
      dropdownObserver(next([RENDER, [], '']));
    }
  });

  dataObserver(subscribe((action) => {
    const [type, data] = action;
    if (type === OPTIONS_ADD) {
      dropdownObserver(next([RENDER, isCanceled ? [] : data, inputValue]));
    } else if (type === OPTIONS_UPDATE) {
      dropdownObserver(next([UPDATE, data]));
    }
  }));

  return [
    inputObserver(bindArg(500, delayOperator)),
    dataObserver,
    dropdownActionObserver
  ];
}

