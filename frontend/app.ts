import { buyApi, searchApi } from "./api";
import { ItemDefinition, CatalogEntry } from "./const";
import { initSelect, OPTIONS_ADD, OPTIONS_UPDATE, OptionsAction, NOT_BUY, TO_BUY, SelectOption, ADD_ITEM, } from "./select/select";
import { asserFalsy } from "./utils/assert";
import { DOM_ERROR, INTERNAL_ERROR } from "./utils/assert";
import { next, subscribe } from "./utils/observer";

const itemToOption = (option: ItemDefinition | CatalogEntry): SelectOption => {
  const isEntry = 'item_definition' in option;
  const item = isEntry ? option.item_definition : option;
  
  const goupFullName = item.group.length ? `${item.group.map(e => e.title).join(", ")}: ` : '';
  const optionName = `${goupFullName}${item.name}`;
  
  return {
    label: optionName,
    value: `${option.pk}`,
    to_buy: isEntry ? option.to_buy : false
  }
};

export const intSelect = (ctx: Window, selector: string) => {
  const label = ctx.document.querySelector(selector);
  asserFalsy(label, DOM_ERROR);
  const input = label.querySelector('input');
  asserFalsy(input, DOM_ERROR);
  const addUrl = ctx.document.querySelector('#create-action');
  const [inputObserver, dataObserver, actionObserver] = initSelect(ctx, input, label);

  actionObserver(subscribe((action) => {
    const [actionType, value] = action;
    if (actionType === ADD_ITEM) {
      ctx.location.href = `${addUrl}?name=${value}`
    }
    if ([TO_BUY, NOT_BUY].includes(actionType)) {
      const pk = Number(value);
      asserFalsy(pk, INTERNAL_ERROR);
      buyApi(ctx, pk, actionType === TO_BUY)
        .then((patchedItem) => {
          const action: OptionsAction = [OPTIONS_UPDATE, [itemToOption(patchedItem)]];
          dataObserver(next(action))
        })
    }
  }));

  inputObserver(subscribe((value) => {
    searchApi(value)
      .then((data) => {
        const selectOptions = data.results.map(itemToOption);
        dataObserver(next([OPTIONS_ADD, selectOptions]))
      });
  }));
}
