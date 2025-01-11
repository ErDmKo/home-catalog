import { bindArg } from './bind';
import { cont } from './cont';

export type ObserverState<EventType> = ((e: EventType) => void)[];
export type ObserverInstance<EventType, ResultType = any> = (
    a: (s: ObserverState<EventType>) => ResultType
) => ResultType;

export const observer = <EventType, ResultType = any>(
    state = [] as ObserverState<EventType>
) => {
    return cont<ObserverState<EventType>, ResultType>(state);
};

export const on = <EventType>(
    callback: (e: EventType) => void,
    state: ObserverState<EventType>
) => {
    state.push(callback);
};


export const trigger = <EventType>(
    event: EventType,
    state: ObserverState<EventType>
) => {
  for (const callback of state) {
    callback(event);
  }
};

// Typescript alias for bindArg(..., trigger);
export const next = <EventType>(e: EventType) => {
  return (state: ObserverState<EventType>) => trigger(e, state);
}

// Typescript alias for bindArg(..., on);
export const subscribe = <EventType>(callback: (e: EventType) => void) => {
  return (state: ObserverState<EventType>) => on(callback, state);
}

export const delayOperator = <T>(delay: number, state: ObserverState<T>) => {
  const oldObserver = observer(state);
  const newObserver = observer<T>();
  let timeOut: number = 0;
  oldObserver(
    bindArg((newVal: T) => {
      clearTimeout(timeOut);
      timeOut = setTimeout(() => {
        newObserver(bindArg(newVal, trigger));
      }, delay);
    }, on)
  );
  return newObserver;
};

export const lazyObserver = <T>(inputObserver: ObserverInstance<T> = observer()) => {
  const outputObserver = observer<T>();
  let lastValue: T;
  inputObserver(subscribe((newVal) => {
    if (lastValue === newVal) {
      return;
    }
    lastValue = newVal;
    outputObserver(next(newVal));
  }));
  return [
    (a: T) => inputObserver(next(a)), 
    (callback: (a: T) => void) =>  outputObserver(subscribe(callback))
  ] as const;
};

export const sumOperator = (state: ObserverState<number>) => {
    const oldObserver = observer(state);
    const newObserver = observer<number>();
    let sum = 0;
    oldObserver(
        bindArg((newVal: number) => {
            sum += newVal;
            newObserver(bindArg(sum, trigger));
        }, on)
    );
    return newObserver;
};

export const combineLatestWith = <First, Second>(
  firstObserver: ObserverInstance<First>,
  secondObserver: ObserverInstance<Second>
) => {
  const newObserver = observer<[First, Second]>();
  let firstValue: First;
  let secondValue: Second;
  firstObserver(subscribe((newVal: First) => {
    firstValue = newVal;
    newObserver(next([firstValue, secondValue]));
  }));
  secondObserver(subscribe((newVal) => {
    secondValue = newVal;
    newObserver(next([firstValue, secondValue]));
  }));
  return newObserver;
};
