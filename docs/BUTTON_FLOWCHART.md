# Подробная схема кнопок RoleHub

Актуально для текущей реализации бота. Документ описывает точки входа, reply-кнопку активной комнаты, текстовые продолжения после кнопок и админские сценарии.

## Легенда

- `[...]` - экран или состояние пользователя.
- `reply-кнопка` - кнопка нижней клавиатуры Telegram.
- `/command` - текстовая команда.
- `текст пользователя` - следующий обычный текст, который обрабатывается через `pending_action`.
- `активный экран` - сообщение, помеченное как главный текущий экран; `/start` и `/clear` его не удаляют.
- `обычное сообщение` - сообщение, которое можно удалить через `/clear`.

## Общие точки входа

```mermaid
flowchart TD
    StartCmd["/start"] --> ClearBeforeStart["Очистить чат: удалить все сохраненные сообщения кроме активного экрана"]
    ClearBeforeStart --> EnsureUser["Создать или обновить пользователя по Telegram ID"]
    EnsureUser --> HasName{"display_name есть?"}
    HasName -- нет --> SetNamePending["pending_action = set_display_name"]
    SetNamePending --> NamePrompt["Экран: ввод имени"]
    HasName -- да --> MainMenu["Главное меню"]

    ClearCmd["/clear"] --> ClearAll["Очистить чат: удалить все сохраненные сообщения кроме активного экрана"]
    ClearAll --> NoScreenChange["Новый экран не показывается"]

    AnyIncoming["Любое входящее сообщение"] --> TrackIncoming["Сохранить message_id для последующей очистки"]
```

## Главное меню

```mermaid
flowchart TD
    Main["Главное меню"]

    Main -->|"🎮 Играть "| Play["Игровое меню"]
    Main -->|"🛍 Магазин "| Shop["Магазин"]
    Main -->|"⚙️ Настройки "| Settings["Настройки"]
    Main -->|"🆘 Поддержка "| Support["Поддержка"]
```

## Игровое меню

Текущий основной путь `menu:play` показывает новое lobby-меню, а не старый экран выбора темы.

```mermaid
flowchart TD
    Play["Игровое меню"]

    Play -->|"🔎 Найти лобби "| FindTopic["Выбор темы для поиска"]
    Play -->|"➕ Создать лобби "| CreateTopic["Выбор темы для создания"]
    Play -->|"⚡ Быстрый вход "| QuickTopic["Выбор темы для быстрого входа"]
    Play -->|"🔑 Войти по коду "| CodePrompt["Экран ввода кода"]
    Play -->|"⬅️ Назад "| Main["Главное меню"]

    FindTopic -->|"⭐ Brawl Stars "| FindBrawl["Поиск свободного Brawl Stars лобби"]
    FindTopic -->|"🦄 My Little Pony "| FindMlp["Поиск свободного MLP лобби"]
    FindTopic -->|"⬅️ Назад "| Play
    FindTopic -->|"🏠 Меню "| Main

    QuickTopic -->|"⭐ Brawl Stars "| QuickBrawl["Быстрое подключение к Brawl Stars"]
    QuickTopic -->|"🦄 My Little Pony "| QuickMlp["Быстрое подключение к MLP"]
    QuickTopic -->|"⬅️ Назад "| Play
    QuickTopic -->|"🏠 Меню "| Main

    CreateTopic -->|"⭐ Brawl Stars "| CreateRole["Выбор роли создателя"]
    CreateTopic -->|"🦄 My Little Pony "| CreateRole
    CreateTopic -->|"⬅️ Назад "| Play
    CreateTopic -->|"🏠 Меню "| Main

    CodePrompt -->|"⬅️ Назад "| Play
    CodePrompt -->|"🏠 Главное меню "| Main
    CodePrompt -->|"текст пользователя"| CodeText["Обработка кода лобби"]
```

## Поиск лобби

```mermaid
flowchart TD
    FindTopic["Выбор темы поиска"] --> FindResult{"Свободное лобби найдено?"}
    FindResult -- да --> FoundLobby["Экран найденного лобби"]
    FindResult -- нет --> NoLobby["Экран: лобби не найдено"]

    FoundLobby -->|"✅ Войти "| JoinStart{"RP-лобби?"}
    JoinStart -- да --> JoinRole["Выбор свободной роли"]
    JoinStart -- нет --> WaitingLobby["Комната ожидания"]
    FoundLobby -->|"🔄 Следующее "| FindNext["Поиск следующего лобби"]
    FoundLobby -->|"⬅️ Назад "| FindTopic
    FoundLobby -->|"🏠 Меню "| Main["Главное меню"]

    NoLobby -->|"➕ Создать лобби "| CreateRole["Выбор роли создателя"]
    NoLobby -->|"🔄 Искать снова "| FindResult
    NoLobby -->|"⬅️ Назад "| FindTopic
    NoLobby -->|"🏠 Меню "| Main
```

## Быстрый вход

```mermaid
flowchart TD
    QuickTopic["Выбор темы быстрого входа"] --> QuickResult{"Свободное лобби найдено?"}
    QuickResult -- нет --> QuickNoLobby["Экран: свободных лобби нет"]
    QuickResult -- да --> QuickRp{"Лобби RP?"}
    QuickRp -- да --> JoinRole["Выбор свободной роли"]
    QuickRp -- нет --> JoinDirect["Подключение без выбора роли"]
    JoinDirect --> AutoStart{"Комната заполнена?"}
    AutoStart -- да --> ActiveLobby["Активная комната"]
    AutoStart -- нет --> WaitingLobby["Комната ожидания"]

    QuickNoLobby -->|"➕ Создать лобби "| CreateRole["Выбор роли создателя"]
    QuickNoLobby -->|"🔄 Искать снова "| QuickResult
    QuickNoLobby -->|"⬅️ Назад "| Play["Игровое меню"]
    QuickNoLobby -->|"🏠 Меню "| Main["Главное меню"]
```

## Вход по коду

```mermaid
flowchart TD
    CodePrompt["Экран ввода кода"] --> SetPendingCode["pending_action = enter_lobby_code"]
    SetPendingCode --> UserText["Пользователь отправляет код текстом"]
    UserText --> CodeFound{"Лобби найдено и доступно?"}
    CodeFound -- нет --> InvalidCode["Ошибка или лобби не найдено"]
    CodeFound -- да --> CodeRp{"RP-лобби?"}
    CodeRp -- да --> JoinRole["Выбор свободной роли"]
    CodeRp -- нет --> WaitingOrActive["Вход в лобби"]

    InvalidCode -->|"🔁 Попробовать еще "| CodePrompt
    InvalidCode -->|"🏠 Главное меню "| Main["Главное меню"]

    WaitingOrActive --> FullAfterJoin{"Комната заполнена?"}
    FullAfterJoin -- да --> ActiveLobby["Активная комната"]
    FullAfterJoin -- нет --> WaitingLobby["Комната ожидания"]
```

## Выбор роли при входе

```mermaid
flowchart TD
    JoinRole["Выбор свободной роли"]
    JoinRole -->|"Роль "| JoinWithRole["Войти с выбранной ролью"]
    JoinRole -->|"🎲 Случайная свободная "| JoinRandom["Войти со случайной свободной ролью"]
    JoinRole -->|"🔎 Найти роль "| JoinRoleSearchPrompt["Ожидание текста поиска роли"]
    JoinRole -->|"◀️ ▶️ "| JoinRolePage["Другая страница ролей"]
    JoinRole -->|"⬅️ Назад "| Play["Игровое меню"]
    JoinRole -->|"🏠 Меню "| Main["Главное меню"]

    JoinRoleSearchPrompt -->|"текст пользователя"| JoinRoleSearchResults{"Свободные роли найдены?"}
    JoinRoleSearchResults -- да --> RoleResults["Список найденных ролей"]
    JoinRoleSearchResults -- нет --> JoinRoleSearchPrompt
    RoleResults -->|"Найденная роль "| JoinWithRole
    RoleResults -->|"🔁 Искать еще "| JoinRoleSearchPrompt
    RoleResults -->|"⬅️ Назад "| JoinRoleSearchPrompt
    RoleResults -->|"🏠 Меню "| Main

    JoinWithRole --> AutoStart{"Комната заполнена?"}
    JoinRandom --> AutoStart
    AutoStart -- да --> ActiveLobby["Активная комната"]
    AutoStart -- нет --> WaitingLobby["Комната ожидания"]
```

## Создание лобби

```mermaid
flowchart TD
    CreateTopic["Выбор темы создания"] --> CreateRole["Выбор роли создателя"]

    CreateRole -->|"Роль "| CreatePrivacy["Выбор приватности"]
    CreateRole -->|"🎲 Случайная "| CreatePrivacy
    CreateRole -->|"🔎 Найти роль "| CreateRoleSearchPrompt["Ожидание текста поиска роли"]
    CreateRole -->|"◀️ ▶️ "| CreateRolePage["Другая страница ролей"]
    CreateRole -->|"⬅️ Назад "| CreateTopic
    CreateRole -->|"🏠 Меню "| Main["Главное меню"]

    CreateRoleSearchPrompt -->|"текст пользователя"| CreateRoleSearchResults{"Роли найдены?"}
    CreateRoleSearchResults -- да --> CreateRoleResults["Список найденных ролей"]
    CreateRoleSearchResults -- нет --> CreateRoleSearchPrompt
    CreateRoleResults -->|"Найденная роль "| CreatePrivacy
    CreateRoleResults -->|"🔁 Искать еще "| CreateRoleSearchPrompt
    CreateRoleResults -->|"⬅️ Назад "| CreateRoleSearchPrompt
    CreateRoleResults -->|"🏠 Меню "| Main

    CreatePrivacy -->|"🌍 Открытое "| CreateConfirm["Подтверждение создания"]
    CreatePrivacy -->|"🔒 Приватное "| CreateConfirm
    CreatePrivacy -->|"⬅️ Назад "| CreateRole
    CreatePrivacy -->|"🏠 Меню "| Main

    CreateConfirm -->|"🚀 Создать лобби "| WaitingLobby["Комната ожидания владельца"]
    CreateConfirm -->|"✏️ Изменить "| CreateTopic
    CreateConfirm -->|"⬅️ Назад "| CreatePrivacy
    CreateConfirm -->|"🏠 Меню "| Main
```

## Комната ожидания

```mermaid
flowchart TD
    WaitingLobby["Комната ожидания"]

    WaitingLobby -->|"🔄 Обновить "| WaitingLobby
    WaitingLobby --> OwnerOnly{"Пользователь владелец?"}
    OwnerOnly -- да --> Invite["📨 Пригласить "]
    OwnerOnly -- да --> StartLobby["▶️ Запустить "]
    OwnerOnly -- да --> CloseLobby["🏁 Закрыть "]

    Invite -->|"приватное"| PrivateInvite["Показать код приватного лобби"]
    Invite -->|"открытое"| PublicInvite["Сообщить, что лобби доступно через поиск"]
    PrivateInvite --> WaitingLobby
    PublicInvite --> WaitingLobby

    StartLobby --> ActiveLobby["Активная комната"]
    CloseLobby --> ClosedLobby["Экран: лобби закрыто"]

    ClosedLobby -->|"🎮 Играть "| Play
    ClosedLobby -->|"🏠 Главное меню "| Main
```

## Активная комната

В активной комнате есть две клавиатуры:

- reply-клавиатура активного экрана комнаты;
- нижняя reply-клавиатура пользователя с кнопками комнаты. Кнопки `/leave` нет, но команда `/leave` работает.

```mermaid
flowchart TD
    ActiveLobby["Активная комната"]

    ActiveLobby -->|"👥 Участники "| Members["Список участников"]
    ActiveLobby -->|"ℹ️ Инфо "| Info["Информация о лобби"]
    ActiveLobby --> OwnerClose{"Пользователь владелец?"}
    OwnerClose -- да -->|"🏁 Закрыть "| ClosedLobby["Экран: лобби закрыто"]

    Info -->|"👥 Участники "| Members
    Info --> OwnerCloseInfo{"Пользователь владелец?"}
    OwnerCloseInfo -- да -->|"🏁 Закрыть "| ClosedLobby

    Members -->|"⬅️ Назад "| Info

    ActiveLobby -->|"обычный текст/фото/стикер/voice"| RelayMessage["Переслать сообщение всем участникам активного лобби"]
```

## Ошибки и специальные lobby-состояния

```mermaid
flowchart TD
    Already["Ошибка: пользователь уже в лобби"]
    Already -->|"Вернуться в лобби "| CurrentInfo["Инфо текущего лобби"]
    Already -->|"🏠 Главное меню "| Main["Главное меню"]

    Full["Ошибка: лобби заполнено"]
    Full -->|"🔎 Найти другое "| FindTopic["Выбор темы поиска"]
    Full -->|"➕ Создать свое "| CreateTopic["Выбор темы создания"]
    Full -->|"🏠 Главное меню "| Main

    Closed["Ошибка: лобби закрыто"]
    Closed --> Play["Игровое меню"]
```

## Настройки

```mermaid
flowchart TD
    Settings["Настройки"]

    Settings -->|"👤 Профиль "| Profile["Настройки профиля"]
    Settings -->|"🔔 Уведомления "| Notifications["Уведомления"]
    Settings -->|"🌐 Язык "| Language["Язык"]
    Settings -->|"🛡 Безопасность "| Safety["Безопасность"]
    Settings -->|"⬅️ Назад "| Main["Главное меню"]

    Profile -->|"✏️ Имя "| NamePrompt["Ожидание ввода имени"]
    Profile -->|"📝 Описание "| ComingBio["Раздел в разработке: описание"]
    Profile -->|"⬅️ Назад "| Settings
    Profile -->|"🏠 Меню "| Main

    NamePrompt -->|"текст пользователя"| SetName{"Имя валидно и уникально?"}
    SetName -- да --> Main
    SetName -- нет --> NamePrompt
    NamePrompt -->|"⏭ Позже "| Main
    NamePrompt -->|"🏠 Главное меню "| Main

    Notifications -->|"✅ Лобби: Вкл "| ComingNotif["Раздел в разработке"]
    Notifications -->|"✅ Приглашения: Вкл "| ComingNotif
    Notifications -->|"✅/❌ Новости "| ToggleNews["Переключить news_notifications_enabled"]
    ToggleNews --> Notifications
    Notifications -->|"⬅️ Назад "| Settings
    Notifications -->|"🏠 Меню "| Main

    Language -->|"🇷🇺 Русский "| ComingLang["Раздел в разработке"]
    Language -->|"⬅️ Назад "| Settings
    Language -->|"🏠 Меню "| Main

    Safety -->|"🚫 Черный список "| ComingSafety["Раздел в разработке"]
    Safety -->|"👁 Приватность профиля "| ComingSafety
    Safety -->|"⚠️ Жалобы "| ComingSafety
    Safety -->|"⬅️ Назад "| Settings
    Safety -->|"🏠 Меню "| Main

    ComingBio -->|"⬅️ Назад "| Profile
    ComingBio -->|"🏠 Главное меню "| Main
    ComingNotif -->|"⬅️ Назад "| Notifications
    ComingNotif -->|"🏠 Главное меню "| Main
    ComingLang -->|"⬅️ Назад "| Language
    ComingLang -->|"🏠 Главное меню "| Main
    ComingSafety -->|"⬅️ Назад "| Safety
    ComingSafety -->|"🏠 Главное меню "| Main
```

## Магазин

```mermaid
flowchart TD
    Shop["Магазин"]

    Shop -->|"👤 Профили "| ShopProfiles["Профили"]
    Shop -->|"🎨 Оформление "| ShopThemes["Оформление"]
    Shop -->|"💎 Премиум "| ShopPremium["Премиум"]
    Shop -->|"🎁 Промокод "| PromoSoon["Раздел в разработке: промокод"]
    Shop -->|"⬅️ Назад "| Main["Главное меню"]

    ShopProfiles -->|"🖼 Аватарки "| AvatarsSoon["Раздел в разработке"]
    ShopProfiles -->|"🏷 Титулы "| TitlesSoon["Раздел в разработке"]
    ShopProfiles -->|"⬅️ Назад "| Shop
    ShopProfiles -->|"🏠 Меню "| Main

    ShopThemes -->|"🌙 Темные стили "| DarkSoon["Раздел в разработке"]
    ShopThemes -->|"✨ Эффекты "| EffectsSoon["Раздел в разработке"]
    ShopThemes -->|"⬅️ Назад "| Shop
    ShopThemes -->|"🏠 Меню "| Main

    ShopPremium -->|"💎 Купить премиум "| BuySoon["Раздел в разработке"]
    ShopPremium -->|"📋 Что входит? "| PremiumInfo["Информация о премиуме"]
    ShopPremium -->|"⬅️ Назад "| Shop
    ShopPremium -->|"🏠 Меню "| Main

    PromoSoon -->|"⬅️ Назад "| Shop
    PromoSoon -->|"🏠 Главное меню "| Main
    AvatarsSoon -->|"⬅️ Назад "| ShopProfiles
    AvatarsSoon -->|"🏠 Главное меню "| Main
    TitlesSoon -->|"⬅️ Назад "| ShopProfiles
    TitlesSoon -->|"🏠 Главное меню "| Main
    DarkSoon -->|"⬅️ Назад "| ShopThemes
    DarkSoon -->|"🏠 Главное меню "| Main
    EffectsSoon -->|"⬅️ Назад "| ShopThemes
    EffectsSoon -->|"🏠 Главное меню "| Main
    BuySoon -->|"⬅️ Назад "| ShopPremium
    BuySoon -->|"🏠 Главное меню "| Main
    PremiumInfo -->|"⬅️ Назад "| ShopPremium
    PremiumInfo -->|"🏠 Главное меню "| Main
```

## Поддержка

```mermaid
flowchart TD
    Support["Поддержка"]

    Support -->|"❓ FAQ "| FAQ["FAQ"]
    Support -->|"Сообщить об ошибке "| BugSoon["Раздел в разработке"]
    Support -->|"👤 Связаться с админом "| AdminSoon["Раздел в разработке"]
    Support -->|"📜 Правила "| Rules["Правила"]
    Support -->|"⬅️ Назад "| Main["Главное меню"]

    FAQ -->|"🎮 Как играть? "| FaqPlay["Ответ FAQ"]
    FAQ -->|"🏠 Что такое лобби? "| FaqLobby["Ответ FAQ"]
    FAQ -->|"🛍 Как работает магазин? "| FaqShop["Ответ FAQ"]
    FAQ -->|"⬅️ Назад "| Support
    FAQ -->|"🏠 Меню "| Main

    BugSoon -->|"⬅️ Назад "| Support
    BugSoon -->|"🏠 Главное меню "| Main
    AdminSoon -->|"⬅️ Назад "| Support
    AdminSoon -->|"🏠 Главное меню "| Main
    Rules -->|"⬅️ Назад "| Support
    Rules -->|"🏠 Главное меню "| Main
    FaqPlay -->|"⬅️ Назад "| FAQ
    FaqPlay -->|"🏠 Главное меню "| Main
    FaqLobby -->|"⬅️ Назад "| FAQ
    FaqLobby -->|"🏠 Главное меню "| Main
    FaqShop -->|"⬅️ Назад "| FAQ
    FaqShop -->|"🏠 Главное меню "| Main
```

## Админ-панель

Доступ к `/admin`, `/users`, `/user`, `/stats`, `/export_users`, `/notify` проверяется по роли `users.role = "admin"` в базе данных.

Доступ к `/makeadmin` и `/removeadmin` проверяется только по `OWNER_IDS` из `.env`.

```mermaid
flowchart TD
    AdminCmd["/admin"] --> IsDbAdmin{"Пользователь admin в БД?"}
    IsDbAdmin -- нет --> SilentDeny["Ничего не показать"]
    IsDbAdmin -- да --> AdminPanel["Админ-панель"]

    AdminPanel -->|"Пользователи "| UsersList["Список последних пользователей"]
    AdminPanel -->|"Статистика "| Stats["Статистика пользователей"]
    AdminPanel -->|"Экспорт CSV "| ExportCsv["Отправить CSV-файл"]
    AdminPanel -->|"Новостная рассылка "| NotifyHelp["Подсказка: /notify текст новости"]
    AdminPanel -->|"Права админов "| RightsHelp["Описание прав доступа"]

    UsersList --> AdminPanel
    Stats --> AdminPanel
    NotifyHelp --> AdminPanel
    RightsHelp --> AdminPanel

    NotifyCmd["/notify текст"] --> NotifyAccess{"Пользователь admin в БД?"}
    NotifyAccess -- нет --> NotifyDeny["Ничего не отправить"]
    NotifyAccess -- да --> HasNotifyText{"Текст есть?"}
    HasNotifyText -- нет --> NotifyUsage["Показать использование команды"]
    HasNotifyText -- да --> SendNews["Разослать новость всем пользователям с Новости: Вкл"]
    SendNews --> NoConfirm["Не отправлять подтверждение админу"]

    MakeAdmin["/makeadmin telegram_id или @username"] --> IsOwner{"Пользователь в OWNER_IDS?"}
    RemoveAdmin["/removeadmin telegram_id или @username"] --> IsOwner
    IsOwner -- нет --> OwnerDeny["Ничего не сделать"]
    IsOwner -- да --> ResolveTarget{"Целевой пользователь найден в БД?"}
    ResolveTarget -- нет --> UsageOrNotFound["Показать usage или что пользователь не найден"]
    ResolveTarget -- да --> ChangeRole["Изменить users.role: admin или user"]
    ChangeRole --> RoleConfirm["Отправить владельцу подтверждение"]
```

## Команды без reply-кнопок

| Команда | Кто может вызвать | Результат |
| --- | --- | --- |
| `/start` | любой пользователь | очищает чат кроме активного экрана, создает/обновляет пользователя, предлагает имя или показывает главное меню |
| `/clear` | любой пользователь | очищает сохраненные сообщения чата кроме активного экрана |
| `/admin` | admin в БД | показывает админ-панель |
| `/users` | admin в БД | показывает последних пользователей |
| `/user <telegram_id>` | admin в БД | показывает карточку пользователя |
| `/stats` | admin в БД | показывает статистику |
| `/export_users` | admin в БД | отправляет CSV с пользователями |
| `/notify <текст>` | admin в БД | рассылает новость пользователям с включенными новостями, без подтверждения отправки |
| `/makeadmin <telegram_id\|@username>` | owner из `.env` | меняет роль пользователя в БД на `admin` |
| `/removeadmin <telegram_id\|@username>` | owner из `.env` | меняет роль пользователя в БД на `user` |

## Текстовые продолжения после кнопок

| Откуда пользователь пришел | pending_action | Следующее сообщение пользователя |
| --- | --- | --- |
| `/start`, если имени нет | `set_display_name` | валидирует уникальное имя, сохраняет `display_name`, затем показывает главное меню |
| Настройки -> Профиль -> Имя | `set_display_name` | валидирует уникальное имя, сохраняет `display_name`, затем показывает главное меню |
| Играть -> Войти по коду | `enter_lobby_code` | ищет лобби по коду, затем предлагает роль или подключает к комнате |
| Создать лобби -> Найти роль | `create_role_search` | ищет роль внутри выбранной темы и показывает результаты |
| Войти в RP-лобби -> Найти роль | `join_role_search:CODE` | ищет свободную роль в конкретном лобби и показывает результаты |

## Особенности очистки и активного экрана

```mermaid
flowchart TD
    Render["Показ нового экрана через _render"] --> SendNewActive["Отправить новое активное сообщение с reply-клавиатурой"]
    SendNewActive --> ActiveSaved

    Clear["/clear или очистка при /start"] --> DeleteClearable["Удалить сохраненные сообщения"]
    DeleteClearable --> PreserveActive["Не удалять активный экран"]

    Notify["/notify"] --> NewsMessages["Новостные сообщения сохраняются как обычные сообщения"]
    NewsMessages --> CanClear["/clear удаляет их тоже"]
```
