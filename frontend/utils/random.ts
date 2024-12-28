declare global {
    interface Window {
        Object: typeof Object;
        Array: typeof Array;
        Math: typeof Math;
    }
}

export const randomRange = (ctx: Window, min: number, max: number) => {
    return min + ctx.Math.random() * (max - min);
};
