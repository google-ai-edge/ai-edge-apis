package com.google.sample.fcdemo.navigation

import androidx.activity.compose.LocalActivity
import androidx.compose.material3.SnackbarDuration
import androidx.compose.material3.SnackbarHostState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.google.sample.fcdemo.activities.MainActivity
import com.google.sample.fcdemo.ui.screens.Fieldset1Screen
import com.google.sample.fcdemo.ui.screens.Fieldset2Screen
import com.google.sample.fcdemo.ui.screens.Fieldset3Screen
import com.google.sample.fcdemo.ui.screens.HomeScreen
import com.google.sample.fcdemo.ui.screens.SummaryScreen
import com.google.sample.fcdemo.viewmodel.FormViewModel
import kotlinx.serialization.Serializable

sealed class Destination {
    @Serializable
    object Home : Destination()

    @Serializable
    object Fieldset1 : Destination()

    @Serializable
    object Fieldset2 : Destination()

    @Serializable
    object Fieldset3 : Destination()

    @Serializable
    object Summary : Destination()
}

class MedicalFormNavigationActions(navController: NavHostController, activity: MainActivity) {
    val exitApplication: () -> Unit = {
        activity.finish()
    }
    val navigateToHome: () -> Unit = {
        navController.popBackStack(Destination.Home, inclusive = false)
    }
    val navigateBack: () -> Unit = {
        navController.popBackStack()
    }
    val navigateToFieldset1: () -> Unit = {
        navController.navigate(Destination.Fieldset1)
    }
    val navigateToFieldset2: () -> Unit = {
        try {
            // Check if the back stack contains the Summary destination
            navController.getBackStackEntry(Destination.Summary)
            navController.navigate(Destination.Summary) {
                popUpTo(Destination.Home) { inclusive = false }
            }
        } catch (e: Exception) {
            // The back stack does not contain the Summary destination
            navController.navigate(Destination.Fieldset2)
        }
    }
    val navigateToFieldset3: () -> Unit = {
        try {
            // Check if the back stack contains the Summary destination
            navController.getBackStackEntry(Destination.Summary)
            navController.navigate(Destination.Summary) {
                popUpTo(Destination.Home) { inclusive = false }
            }
        } catch (e: Exception) {
            // The back stack does not contain the Summary destination
            navController.navigate(Destination.Fieldset3)
        }
    }
    val reviseFieldset1: () -> Unit = {
        navController.navigate(Destination.Fieldset1) {
            popUpTo(Destination.Summary) { inclusive = false }
        }
    }
    val reviseFieldset2: () -> Unit = {
        navController.navigate(Destination.Fieldset2) {
            popUpTo(Destination.Summary) { inclusive = false }
        }
    }
    val reviseFieldset3: () -> Unit = {
        navController.navigate(Destination.Fieldset3) {
            popUpTo(Destination.Summary) { inclusive = false }
        }
    }
    val navigateToSummary: () -> Unit = {
        navController.navigate(Destination.Summary) {
            popUpTo(Destination.Home) { inclusive = false }
        }
    }
}

@Composable
fun MedicalFormNavHost(formViewModel: FormViewModel) {
    val activity = LocalActivity.current as MainActivity
    val navController = rememberNavController()
    val navigationActions = remember(navController) {
        MedicalFormNavigationActions(navController, activity)
    }
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(Unit) {
        formViewModel.errorEvent.collect { errorMsg ->
            snackbarHostState.showSnackbar(
                message = errorMsg,
                duration = SnackbarDuration.Short,
                withDismissAction = true
            )
        }
    }

    NavHost(navController = navController, startDestination = Destination.Home) {
        composable<Destination.Home> {
            HomeScreen(
                viewModel = formViewModel,
                snackbarHostState = snackbarHostState,
                navigationActions = navigationActions,
            )
        }
        composable<Destination.Fieldset1> {
            Fieldset1Screen(
                viewModel = formViewModel,
                snackbarHostState = snackbarHostState,
                navigationActions = navigationActions,
            )
        }
        composable<Destination.Fieldset2> {
            Fieldset2Screen(
                viewModel = formViewModel,
                snackbarHostState = snackbarHostState,
                navigationActions = navigationActions,
            )
        }
        composable<Destination.Fieldset3> {
            Fieldset3Screen(
                viewModel = formViewModel,
                snackbarHostState = snackbarHostState,
                navigationActions = navigationActions,
            )
        }
        composable<Destination.Summary> {
            SummaryScreen(
                viewModel = formViewModel,
                snackbarHostState = snackbarHostState,
                navigationActions = navigationActions,
            )
        }
    }
}