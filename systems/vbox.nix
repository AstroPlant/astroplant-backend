{
  database = {
    deployment.targetEnv = "virtualbox";
    deployment.virtualbox.memorySize = 2048;
    deployment.virtualbox.headless = true;
  };

  kafka = {
    deployment.targetEnv = "virtualbox";
    deployment.virtualbox.memorySize = 2048;
    deployment.virtualbox.headless = true;
  };

  mqtt = {
    deployment.targetEnv = "virtualbox";
    deployment.virtualbox.memorySize = 2048;
    deployment.virtualbox.headless = true;
  };
}
