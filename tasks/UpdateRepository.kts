import java.io.File

fun runBashScript(scriptPath: String) {
    val process = ProcessBuilder("bash", scriptPath)
        .directory(File(scriptPath).parentFile) // Set working directory to script's location
        .redirectOutput(ProcessBuilder.Redirect.INHERIT)
        .redirectError(ProcessBuilder.Redirect.INHERIT)
        .start()

    val exitCode = process.waitFor()
    if (exitCode != 0) {
        throw RuntimeException("Script execution failed with exit code $exitCode")
    }
}

fun main() {
    val scriptPath = "scripts/test.sh"
    println("Running Bash script: $scriptPath")
//    runBashScript(scriptPath)
    println("Bash script completed.")
}