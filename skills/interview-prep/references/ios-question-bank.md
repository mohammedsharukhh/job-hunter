# iOS interview question bank (pick by JD and level)

## Swift language
- Value vs reference types; when to use struct vs class vs actor
- Optionals, optional chaining, `guard` vs `if let`
- ARC, strong/weak/unowned, retain cycles in closures (`[weak self]`)
- Protocols, protocol extensions, associated types, `some` vs `any`
- Generics and constraints; `Codable` customisation
- Copy-on-write; `inout`; escaping vs non-escaping closures
- Error handling: `throws`, `Result`, typed throws

## Concurrency
- GCD vs OperationQueue vs Swift Concurrency
- `async/await`, `Task`, task groups, cancellation
- Actors, `@MainActor`, `Sendable`, data races
- Deadlocks, race conditions, thread-safe caches

## UI
- UIKit view lifecycle; SwiftUI view lifecycle and identity
- `@State`, `@Binding`, `@StateObject` vs `@ObservedObject`, `@Observable`, `@Environment`
- Auto Layout, intrinsic content size; SwiftUI layout process
- Table/collection view performance, diffable data sources, cell reuse
- Navigation (NavigationStack, coordinators), deep links, universal links

## Architecture
- MVC vs MVVM vs VIPER vs TCA — trade-offs
- Dependency injection, modularisation (SPM packages)
- Offline-first, caching, Core Data / SwiftData / Realm
- Clean networking layer: URLSession, retry, auth token refresh

## Platform & integrations
- Push notifications (APNs, silent push), background tasks
- OAuth / Sign in with Apple / Firebase Auth; Keychain storage
- In-app purchases, StoreKit 2, receipt validation
- App Store review guidelines, TestFlight, phased release
- Privacy manifests, ATT

## Quality & performance
- Unit/UI testing (XCTest, Swift Testing), mocking, snapshot tests
- Instruments: Time Profiler, Leaks, Allocations; launch time; jank
- Crash triage (Crashlytics), symbolication
- CI/CD: Fastlane, Xcode Cloud, GitHub Actions; code signing

## Mobile system design prompts
- Design an image feed with infinite scroll and offline cache
- Design a chat app client (sync, ordering, retries, push)
- Design a media upload pipeline with background resume
- Design feature flags / remote config for an app

## DSA patterns most asked for mobile roles
Arrays & hashing, two pointers, sliding window, stack, binary search, linked list, trees (BFS/DFS), heaps/top-K, intervals, simple DP (climbing stairs, house robber, LIS), graphs (islands, topological sort).
