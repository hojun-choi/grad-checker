rootProject.name = "grad-checker"

pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    // 프로젝트에서 repositories 선언을 안 쓰고 settings의 것을 쓰도록 고정
    repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)
    repositories {
        mavenCentral()
    }
}
