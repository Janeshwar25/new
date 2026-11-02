<?xml version="1.0" encoding="UTF-8"?>

<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
-->

<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">

    <localRepository>${user.home}/.m2/repo1/m3-3.6.3</localRepository>

    <mirrors>
        <mirror>
            <id>artifactory</id>
            <name>Artifactory Maven Virtual</name>
            <url>https://edgeinternal1uhg.optum.com/artifactory/glb-maven-vir</url>
            <mirrorOf>*,!optum-np-releases</mirrorOf>
        </mirror>
    </mirrors>

    <servers>
        <server>
            <id>artifactory</id>
            <username>${env.MAVEN_USER}</username>
            <password>${env.MAVEN_PASSWORD}</password>
        </server>
        <server>
            <id>optum-np-releases</id>
            <username>${env.MAVEN_USER}</username>
            <password>${env.MAVEN_PASSWORD}</password>
        </server>
    </servers>

    <profiles>
        <profile>
            <id>artifactory</id>
            <repositories>
                <repository>
                    <id>central</id>
                    <name>Maven Releases</name>
                    <url>https://edgeinternal1uhg.optum.com/artifactory/glb-maven-vir</url>
                    <releases>
                        <enabled>true</enabled>
                        <updatePolicy>never</updatePolicy>
                        <checksumPolicy>warn</checksumPolicy>
                    </releases>
                    <snapshots>
                        <enabled>false</enabled>
                    </snapshots>
                </repository>
                <repository>
                    <id>snapshots</id>
                    <name>Maven Snapshots</name>
                    <url>https://edgeinternal1uhg.optum.com/artifactory/glb-maven-vir</url>
                    <releases>
                        <enabled>false</enabled>
                    </releases>
                    <snapshots>
                        <enabled>true</enabled>
                        <updatePolicy>always</updatePolicy>
                        <checksumPolicy>warn</checksumPolicy>
                    </snapshots>
                </repository>
                <repository>
                    <id>optum-np-releases</id>
                    <name>Optum DSS NP Releases</name>
                    <url>https://edgeinternal1uhg.optum.com:443/artifactory/dataselfservice-maven-np-releases-loc/</url>
                    <releases>
                        <enabled>true</enabled>
                        <updatePolicy>never</updatePolicy>
                        <checksumPolicy>warn</checksumPolicy>
                    </releases>
                    <snapshots>
                        <enabled>false</enabled>
                    </snapshots>
                </repository>
            </repositories>
            <pluginRepositories>
                <pluginRepository>
                    <id>central</id>
                    <name>Maven Plugin Releases</name>
                    <url>https://edgeinternal1uhg.optum.com/artifactory/glb-maven-vir</url>
                    <releases>
                        <enabled>true</enabled>
                        <updatePolicy>never</updatePolicy>
                        <checksumPolicy>warn</checksumPolicy>
                    </releases>
                    <snapshots>
                        <enabled>false</enabled>
                    </snapshots>
                </pluginRepository>
                <pluginRepository>
                    <id>snapshots</id>
                    <name>Maven Plugin Snapshots</name>
                    <url>https://edgeinternal1uhg.optum.com/artifactory/glb-maven-vir</url>
                    <releases>
                        <enabled>false</enabled>
                    </releases>
                    <snapshots>
                        <enabled>true</enabled>
                        <updatePolicy>always</updatePolicy>
                        <checksumPolicy>warn</checksumPolicy>
                    </snapshots>
                </pluginRepository>
            </pluginRepositories>
        </profile>
    </profiles>
    <activeProfiles>
        <activeProfile>artifactory</activeProfile>
    </activeProfiles>
</settings>
