# Changelog

## [1.0.1](https://github.com/reedr/ha-watts-home/compare/v1.1.2...v1.0.1) (2026-09-30)


### Features

* add humidity control for Tekmar 563 with humidifier/dehumidifier setpoints ([94a1c66](https://github.com/reedr/ha-watts-home/commit/94a1c6662e4af25cc8a87ce8494e30df485f1f4c))
* add Pydantic v2 models for Watts API device responses ([82de425](https://github.com/reedr/ha-watts-home/commit/82de425b5229485a4ef4b28ff9ff8dfa430ee99c))
* add reauthentication flow to the config flow ([#9](https://github.com/reedr/ha-watts-home/issues/9)) ([cd1cbac](https://github.com/reedr/ha-watts-home/commit/cd1cbac2afb2a1c987b533c7ed18e4909186dfde))
* add room temperature sensor for long-term statistics ([#5](https://github.com/reedr/ha-watts-home/issues/5)) ([1c6d0fb](https://github.com/reedr/ha-watts-home/commit/1c6d0fba839fab83412faba6b191fc88a39a7dc2))
* climate entity uses typed WattsDevice lookup and dynamic discovery listener ([edb6d21](https://github.com/reedr/ha-watts-home/commit/edb6d2101f7f8d22ea0c8bf5e9ec90da811f370d))
* coordinator stores devices as dict[str, WattsDevice] for O(1) lookup ([4b2922d](https://github.com/reedr/ha-watts-home/commit/4b2922d966952fc35bd93af8a75eee38df1dff9e))
* extended entity support for Tekmar 5xx thermostats ([cf1813e](https://github.com/reedr/ha-watts-home/commit/cf1813e5372b9ce2f3fcc34edda4acab051948f1))
* initial repo scaffold ([f4a8227](https://github.com/reedr/ha-watts-home/commit/f4a8227c835d8eec53fd9a51b01dd387bd63b714))
* sensor entities use typed WattsDevice lookup and dynamic discovery listener ([7691ede](https://github.com/reedr/ha-watts-home/commit/7691edea67bdccf3aef6e4d0f7dbcb2231e91723))
* validate devices with Pydantic at API boundary in get_devices() ([e10e47b](https://github.com/reedr/ha-watts-home/commit/e10e47b3a167b17eef2e5fb2214c2bfb80472f19))


### Bug Fixes

* guard against null device data field and stale availability ([f575db8](https://github.com/reedr/ha-watts-home/commit/f575db8e2e7b21a4b430bd3cb70f25b0911437d7))
* guard against null device data fields in climate helpers ([013ddd3](https://github.com/reedr/ha-watts-home/commit/013ddd3fd0a319bfa39af7248b7368f574ee2363))
* guard against null device data fields in climate helpers ([85f9554](https://github.com/reedr/ha-watts-home/commit/85f95548f1db562b81b87a28800615dc56dc4fd5))
* keep the floor entity's upper setpoint bound usable ([#17](https://github.com/reedr/ha-watts-home/issues/17)) ([412f70d](https://github.com/reedr/ha-watts-home/commit/412f70dca25d6bd477ef22c9619cb8650c7f4060))
* **models:** make WattsTarget.min/max/steps optional for SnowMelt controls ([#3](https://github.com/reedr/ha-watts-home/issues/3)) ([7e6cf3b](https://github.com/reedr/ha-watts-home/commit/7e6cf3b08976a247fa55fd0d8bcbf1050ae3cb64))
* poll devices from every Watts Home location ([#25](https://github.com/reedr/ha-watts-home/issues/25)) ([dd36a37](https://github.com/reedr/ha-watts-home/commit/dd36a37f0cd49b3df41027a99fd0ac4d6ffbea9c))
* retry transient 5xx from the auth server ([#7](https://github.com/reedr/ha-watts-home/issues/7)) ([087c73a](https://github.com/reedr/ha-watts-home/commit/087c73a6538114a77b3a954ebc178620d61c2fb5))
* support Tekmar devices which are missing low/high setpoint ([#15](https://github.com/reedr/ha-watts-home/issues/15)) ([cfae065](https://github.com/reedr/ha-watts-home/commit/cfae0658dd65d5f9df3e0c48fc8548a4bc3e39ea))
* support the Tekmar 170 Wi-Fi Setpoint Control ([#21](https://github.com/reedr/ha-watts-home/issues/21)) ([c67c39c](https://github.com/reedr/ha-watts-home/commit/c67c39c1c38cfce657598a9d17d73107c623c107))


### Miscellaneous Chores

* release 1.0.0 ([f658e4f](https://github.com/reedr/ha-watts-home/commit/f658e4f951586464b932f6a450483674ec2b803a))
* release 1.0.1 ([b372338](https://github.com/reedr/ha-watts-home/commit/b3723384edafdd234d555edf94232531cf4c39b1))

## [1.1.2](https://github.com/bhamiltoncx/ha-watts-home/compare/v1.1.1...v1.1.2) (2026-09-15)


### Bug Fixes

* poll devices from every Watts Home location ([#25](https://github.com/bhamiltoncx/ha-watts-home/issues/25)) ([dd36a37](https://github.com/bhamiltoncx/ha-watts-home/commit/dd36a37f0cd49b3df41027a99fd0ac4d6ffbea9c))

## [1.1.1](https://github.com/bhamiltoncx/ha-watts-home/compare/v1.1.0...v1.1.1) (2026-08-23)


### Bug Fixes

* keep the floor entity's upper setpoint bound usable ([#17](https://github.com/bhamiltoncx/ha-watts-home/issues/17)) ([412f70d](https://github.com/bhamiltoncx/ha-watts-home/commit/412f70dca25d6bd477ef22c9619cb8650c7f4060))
* support Tekmar devices which are missing low/high setpoint ([#15](https://github.com/bhamiltoncx/ha-watts-home/issues/15)) ([cfae065](https://github.com/bhamiltoncx/ha-watts-home/commit/cfae0658dd65d5f9df3e0c48fc8548a4bc3e39ea))
* support the Tekmar 170 Wi-Fi Setpoint Control ([#21](https://github.com/bhamiltoncx/ha-watts-home/issues/21)) ([c67c39c](https://github.com/bhamiltoncx/ha-watts-home/commit/c67c39c1c38cfce657598a9d17d73107c623c107))

## [1.1.0](https://github.com/bhamiltoncx/ha-watts-home/compare/v1.0.1...v1.1.0) (2026-08-07)


### Features

* add reauthentication flow to the config flow ([#9](https://github.com/bhamiltoncx/ha-watts-home/issues/9)) ([cd1cbac](https://github.com/bhamiltoncx/ha-watts-home/commit/cd1cbac2afb2a1c987b533c7ed18e4909186dfde))


### Bug Fixes

* retry transient 5xx from the auth server ([#7](https://github.com/bhamiltoncx/ha-watts-home/issues/7)) ([087c73a](https://github.com/bhamiltoncx/ha-watts-home/commit/087c73a6538114a77b3a954ebc178620d61c2fb5))
