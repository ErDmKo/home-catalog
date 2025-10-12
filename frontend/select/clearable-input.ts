import { domCreator, genProp, genRef, genTagDiv, genText } from "../utils/dom";
import { next, observer, subscribe } from "../utils/observer";
import type { ObserverInstance } from "../utils/observer";

const BUTTON_SIZE = '44px';

const clearButtonStyle = {
  position: 'absolute',
  top: '0',
  right: '0',
  width: BUTTON_SIZE,
  height: '100%',  // Match input height exactly
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  cursor: 'pointer',
  fontSize: '24px',
  color: '#666',
  backgroundColor: 'transparent',
  border: 'none',
  userSelect: 'none',
};

export const makeClearable = (
  ctx: Window,
  wrapper: HTMLElement,
  inputValueObserver: ObserverInstance<string>
): void => {
  const buttonTemplate = genTagDiv([
    genProp('style', clearButtonStyle),
    genText('×'),
    genProp('onclick', () => {
      inputValueObserver(next(''));
    }),
    genRef()  // Mark this element to be returned from domCreator for show/hide logic
  ], []);

  const [buttonElement] = domCreator(ctx, wrapper, buttonTemplate);

  buttonElement.style.display = 'none';

  // Subscribe to input value changes to show/hide button
  const visibilityObserver = observer<string>();
  visibilityObserver(subscribe((value) => {
    buttonElement.style.display = value ? 'flex' : 'none';
  }));

  // Connect to the input value observer to read values
  inputValueObserver(subscribe((value) => {
    visibilityObserver(next(value));
  }));
};
