/**
 * Precompiled [buildlogic.mps-conventions.gradle.kts][Buildlogic_mps_conventions_gradle] script plugin.
 *
 * @see Buildlogic_mps_conventions_gradle
 */
public
class Buildlogic_mpsConventionsPlugin : org.gradle.api.Plugin<org.gradle.api.Project> {
    override fun apply(target: org.gradle.api.Project) {
        try {
            Class
                .forName("Buildlogic_mps_conventions_gradle")
                .getDeclaredConstructor(org.gradle.api.Project::class.java, org.gradle.api.Project::class.java)
                .newInstance(target, target)
        } catch (e: java.lang.reflect.InvocationTargetException) {
            throw e.targetException
        }
    }
}
