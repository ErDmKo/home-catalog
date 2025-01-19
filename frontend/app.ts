import { buyApi, searchApi } from "./api";
import { CatalogItem } from "./appType";
import { initSelect, OPTIONS_ADD, OPTIONS_UPDATE, OptionsAction, PATH_TO_BUY, SelectOption, } from "./select/select";
import { asserFalsy } from "./utils/assert";
import { DOM_ERROR, INTERNAL_ERROR } from "./utils/assert";
import { next, subscribe } from "./utils/observer";

const itemToOption = (option: CatalogItem): SelectOption => {
  const goupFullName = option.group.length ? `${option.group.map(e => e.title).join(", ")}: ` : '';
  const optionName = `${goupFullName}${option.name}`;
  return {
    label: optionName,
    value: `${option.pk}`,
    to_buy: option.to_buy
  }
};

export const intSelect = (ctx: Window, selector: string) => {
  const label = document.querySelector(selector);
  asserFalsy(label, DOM_ERROR);
  const input = label.querySelector('input');
  asserFalsy(input, DOM_ERROR);

  const [inputObserver, dataObserver, actionObserver] = initSelect(ctx, input, label);

  actionObserver(subscribe((action) => {
    const [actionType, value] = action;
    const pk = Number(value);
    asserFalsy(pk, INTERNAL_ERROR);
    buyApi(ctx, pk, actionType === PATH_TO_BUY)
      .then((patchedItem) => {
        const action: OptionsAction = [OPTIONS_UPDATE, [itemToOption(patchedItem)]];
        dataObserver(next(action))
      })
  }));

  inputObserver(subscribe((value) => {
    searchApi(value)
      .then((data) => {
        const selectOptions = data.results.map(itemToOption);
        dataObserver(next([OPTIONS_ADD, selectOptions]))
      });
  }));
}
