export const PROP = 0 as const;
export const REF = 1 as const;
export const ATTR = 2 as const;

type PropType = string | Function | Partial<CSSStyleDeclaration> | number

type Props =
    | readonly [type: typeof ATTR, key: string, value: string | number]
    | readonly [type: typeof PROP, key: string, value: PropType]
    | readonly [type: typeof REF] ;

type TagName = keyof HTMLElementTagNameMap;

export type DOMStruct<K extends TagName> = readonly [
    tag: K,
    attributes: readonly Props[],
    children?: readonly DOMStruct<K>[]
];

function genPropFn (name: 'style', value: Partial<CSSStyleDeclaration>): Props;
function genPropFn (name: 'onclick', value: (m: MouseEvent) => void): Props;
function genPropFn (name: string, value: PropType): Props;
function genPropFn (name: string, value:  PropType) {
  return [PROP, name, value] as const;
};

export const genProp = genPropFn;

export const genAttr = (name: string, value: string | number): Props => {
  return [ATTR, name, value] as const;
};

export const genRef = (): Props => [REF] as const;

export const genText = (text: string | number): Props => {
  return [PROP, 'innerText', text] as const
};

export const genClass = (className: string): Props => {
  return [ATTR, 'class', className] as const
}

export const genTagDiv = <T extends TagName>(
  props: Props[],
  children: DOMStruct<T>[] = [],
): DOMStruct<T> => {
  return ['div' as T, props, children] as const;
};

export const genTagName = <T extends TagName>(
  tagName: T,
  props: Props[],
  children: DOMStruct<T>[] = []
): DOMStruct<T> => { 
  return [tagName, props, children] as const;
};

const isFragment = <T extends TagName>(struct: DOMStruct<T> | DOMStruct<T>[]): struct is DOMStruct<T>[] => {
  return struct.length > 0 && Array.isArray(struct[0]);
}

export const domCreator = <K extends keyof HTMLElementTagNameMap>(
    ctx: Window,
    root: Element,
    struct: DOMStruct<K> | DOMStruct<K>[]
): HTMLElementTagNameMap[K][] => {
    if (!(ctx.document && typeof ctx.document.createElement == 'function')) {
        throw new Error();
    }
    const currnent: [Element, DOMStruct<K>][] = isFragment(struct) 
      ? struct.reverse()
          .map((s) => [root, s])
      : [[root, struct]];
    const refs: HTMLElementTagNameMap[K][] = [];
    while (currnent.length) {
        const nextStruct = currnent.pop();
        if (!nextStruct) {
            break;
        }
        const [root, struct] = nextStruct;
        const [tag, attributes, children] = struct;
        const element = ctx.document.createElement(tag);
        for (const [type, key, value] of attributes) {
            if (type === REF) {
                refs.push(element);
            } else if (type === PROP) {
                if (key === 'style') {
                    Object.assign(element.style, value);
                } else {
                    (element as any)[key] = value;
                }
            } else {
                element.setAttribute(key, `${value}`);
            }
        }
        root.appendChild(element);
        (children || []).forEach((child) => {
            currnent.unshift([element, child]);
        });
    }
    return refs;
};

export const cleanHtml = (root: HTMLElement) => {
    while (root.firstChild) {
        root.removeChild(root.firstChild);
    }
}
