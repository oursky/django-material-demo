import * as React from "react";
import * as ReactDOM from "react-dom/client";
import Switch from "@mui/material/Switch";
import createCache from "@emotion/cache";
import { CacheProvider } from "@emotion/react";

// How to create custom form control elements:
// https://web.dev/more-capable-form-controls/#defining-a-form-associated-custom-element
class AppSwitch extends HTMLElement {
  internals: ElementInternals;
  private _value: boolean;

  static get formAssociated() {
    return true;
  }

  get name() {
    return this.getAttribute("name");
  }
  get value() {
    return this._value;
  }
  set value(v) {
    this._value = v;
    this.internals.setFormValue(String(this._value));
  }

  constructor() {
    super();
    this.internals = this.attachInternals();
    this._value = false;
  }

  _onSwitchChange = (
    _: React.ChangeEvent<HTMLInputElement>,
    checked: boolean
  ) => {
    this.value = checked;
  };

  connectedCallback() {
    const emotionRoot = document.createElement("style");
    const cache = createCache({
      key: "css",
      prepend: true,
      container: emotionRoot,
    });
    const mountPoint = document.createElement("div");
    const shadow = this.attachShadow({ mode: "open" });
    shadow.appendChild(mountPoint);
    shadow.appendChild(emotionRoot);
    const root = ReactDOM.createRoot(mountPoint);
    this.value = this.getAttribute("checked") === null ? false : true;

    root.render(
      <CacheProvider value={cache}>
        <Switch defaultChecked={this._value} onChange={this._onSwitchChange} />
      </CacheProvider>
    );
  }

  disconnectedCallback() {}
}

window.addEventListener("load", () => {
  window.customElements.define("app-switch", AppSwitch);
});
