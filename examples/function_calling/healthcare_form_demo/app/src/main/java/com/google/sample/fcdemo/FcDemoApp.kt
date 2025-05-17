package com.google.sample.fcdemo

import android.app.Application
import android.content.Context

class FcDemoApp : Application() {
    override fun onCreate() {
        super.onCreate()
        appContext = applicationContext
    }

    companion object {
        lateinit var appContext: Context
    }
}