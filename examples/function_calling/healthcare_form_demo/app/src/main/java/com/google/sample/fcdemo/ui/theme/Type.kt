package com.google.sample.fcdemo.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import com.google.sample.fcdemo.R

val AppDefault = FontFamily(
    Font(R.font.demo_standard, FontWeight.Normal)
)

val Hero = FontFamily(
    Font(R.font.product_name, FontWeight.Normal)
)

private val defaultTypography = Typography()
val Typography: Typography = Typography(

    displayLarge = defaultTypography.displayLarge.copy(fontFamily = AppDefault),
    displayMedium = defaultTypography.displayMedium.copy(fontFamily = AppDefault),
    displaySmall = defaultTypography.displaySmall.copy(fontFamily = AppDefault),

    headlineLarge = defaultTypography.headlineLarge.copy(fontSize = 44.sp, fontFamily = Hero),
    headlineMedium = defaultTypography.headlineMedium.copy(fontSize = 35.sp, fontFamily = Hero),
    headlineSmall = defaultTypography.headlineSmall.copy(fontSize = 30.sp, fontFamily = Hero),

    titleLarge = defaultTypography.titleLarge.copy(fontSize = 26.sp, fontFamily = AppDefault),
    titleMedium = defaultTypography.titleMedium.copy(fontFamily = AppDefault),
    titleSmall = defaultTypography.titleSmall.copy(fontFamily = AppDefault),

    bodyLarge = defaultTypography.bodyLarge.copy(fontSize = 22.sp, fontFamily = AppDefault),
    bodyMedium = defaultTypography.bodyMedium.copy(fontSize = 18.sp, fontFamily = AppDefault),
    bodySmall = defaultTypography.bodySmall.copy(fontFamily = AppDefault),

    labelLarge = defaultTypography.labelLarge.copy(fontSize = 18.sp, fontFamily = AppDefault),
    labelMedium = defaultTypography.labelMedium.copy(fontSize = 14.sp, fontFamily = AppDefault),
    labelSmall = defaultTypography.labelSmall.copy(fontFamily = AppDefault),

)