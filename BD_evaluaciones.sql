-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: evaluaciones
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alumnx_materia`
--

DROP TABLE IF EXISTS `alumnx_materia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alumnx_materia` (
  `id_alumnx` int(11) NOT NULL,
  `id_course` int(11) NOT NULL,
  PRIMARY KEY (`id_alumnx`,`id_course`),
  KEY `alumnx_materia_ibfk_2` (`id_course`),
  CONSTRAINT `alumnx_materia_ibfk_1` FOREIGN KEY (`id_alumnx`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `alumnx_materia_ibfk_2` FOREIGN KEY (`id_course`) REFERENCES `materia` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alumnx_materia`
--

LOCK TABLES `alumnx_materia` WRITE;
/*!40000 ALTER TABLE `alumnx_materia` DISABLE KEYS */;
INSERT INTO `alumnx_materia` VALUES (2,1),(4,1),(4,2),(4,15),(5,4),(37,4);
/*!40000 ALTER TABLE `alumnx_materia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `answer`
--

DROP TABLE IF EXISTS `answer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `answer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `response_id` int(11) DEFAULT NULL,
  `id_question` int(11) DEFAULT NULL,
  `choice_id` int(11) DEFAULT NULL,
  `texto_respuesta` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `answer_ibfk_1` (`id_question`),
  KEY `fk_answer_choice` (`choice_id`),
  KEY `fk_answer_response` (`response_id`),
  CONSTRAINT `answer_ibfk_1` FOREIGN KEY (`id_question`) REFERENCES `question` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_answer_choice` FOREIGN KEY (`choice_id`) REFERENCES `choice` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_answer_response` FOREIGN KEY (`response_id`) REFERENCES `response` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=162 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `answer`
--

LOCK TABLES `answer` WRITE;
/*!40000 ALTER TABLE `answer` DISABLE KEYS */;
INSERT INTO `answer` VALUES (30,15,43,142,'El docente explica los conceptos claramente.'),(31,15,44,147,'El docente fomenta la participación.'),(32,15,45,150,'El docente domina el contenido.'),(33,15,46,155,'Los recursos son adecuados.'),(34,15,47,159,'El docente muestra interés por el aprendizaje.'),(35,15,48,NULL,'test'),(36,16,43,144,'El docente explica los conceptos claramente.'),(37,16,44,148,'El docente fomenta la participación.'),(38,16,45,151,'El docente domina el contenido.'),(39,16,46,153,'Los recursos son adecuados.'),(40,16,47,159,'El docente muestra interés por el aprendizaje.'),(41,16,48,NULL,'No me gusta su forma de dar clases.'),(108,28,49,161,'El docente explica los conceptos claramente.'),(109,28,50,165,'El docente fomenta la participación.'),(110,28,51,169,'El docente domina el contenido.'),(111,28,52,173,'Los recursos son adecuados.'),(112,28,53,177,'El docente muestra interés por el aprendizaje.'),(113,28,54,NULL,'Prueba automatizada: todo bien.'),(114,29,43,144,'El docente explica los conceptos claramente.'),(115,29,44,145,'El docente fomenta la participación.'),(116,29,45,151,'El docente domina el contenido.'),(117,29,46,154,'Los recursos son adecuados.'),(118,29,47,159,'El docente muestra interés por el aprendizaje.'),(119,29,48,NULL,'k'),(126,31,37,122,'El docente explica los conceptos claramente.'),(127,31,38,127,'El docente fomenta la participación.'),(128,31,39,129,'El docente domina el contenido.'),(129,31,40,136,'Los recursos son adecuados.'),(130,31,41,138,'El docente muestra interés por el aprendizaje.'),(131,31,42,NULL,'el docente se la paso hablando del indice j todo el semestre, muy mal'),(150,35,139,462,'Los temas son interesantes'),(151,35,140,467,'El semestre es suficiente para abarcar lo necesario'),(152,35,141,470,'El temario es completo.'),(153,35,142,475,'Los recursos son adecuados.'),(154,35,143,478,'Me interesa el contenido de la materia.'),(155,35,144,NULL,'2aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),(156,36,37,122,'El docente explica los conceptos claramente.'),(157,36,38,127,'El docente fomenta la participación.'),(158,36,39,130,'El docente domina el contenido.'),(159,36,40,135,'Los recursos son adecuados.'),(160,36,41,138,'El docente muestra interés por el aprendizaje.'),(161,36,42,NULL,'ssssssssssssssssssssssssssssss123423432094()/&%$#\"$%&/()UIJHJgytfR6ts65+ewjweod/*asdjksjadlasjksjdoiwqu09e32787y39y8u3e02980932807e389yruhewu0q9388888899999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999');
/*!40000 ALTER TABLE `answer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `choice`
--

DROP TABLE IF EXISTS `choice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `choice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_question` int(11) NOT NULL,
  `choice_text` varchar(255) NOT NULL,
  `sort_order` int(11) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `fk_choice_question` (`id_question`),
  CONSTRAINT `choice_ibfk_1` FOREIGN KEY (`id_question`) REFERENCES `question` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_choice_question` FOREIGN KEY (`id_question`) REFERENCES `question` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=501 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `choice`
--

LOCK TABLES `choice` WRITE;
/*!40000 ALTER TABLE `choice` DISABLE KEYS */;
INSERT INTO `choice` VALUES (1,1,'Muy de acuerdo',1),(2,1,'De acuerdo',2),(3,1,'En desacuerdo',3),(4,1,'Muy en desacuerdo',4),(5,2,'Muy de acuerdo',1),(6,2,'De acuerdo',2),(7,2,'En desacuerdo',3),(8,2,'Muy en desacuerdo',4),(9,3,'Muy de acuerdo',1),(10,3,'De acuerdo',2),(11,3,'En desacuerdo',3),(12,3,'Muy en desacuerdo',4),(13,4,'Muy de acuerdo',1),(14,4,'De acuerdo',2),(15,4,'En desacuerdo',3),(16,4,'Muy en desacuerdo',4),(17,5,'Muy de acuerdo',1),(18,5,'De acuerdo',2),(19,5,'En desacuerdo',3),(20,5,'Muy en desacuerdo',4),(21,7,'Muy de acuerdo',1),(22,7,'De acuerdo',2),(23,7,'En desacuerdo',3),(24,7,'Muy en desacuerdo',4),(25,8,'Muy de acuerdo',1),(26,8,'De acuerdo',2),(27,8,'En desacuerdo',3),(28,8,'Muy en desacuerdo',4),(29,9,'Muy de acuerdo',1),(30,9,'De acuerdo',2),(31,9,'En desacuerdo',3),(32,9,'Muy en desacuerdo',4),(33,10,'Muy de acuerdo',1),(34,10,'De acuerdo',2),(35,10,'En desacuerdo',3),(36,10,'Muy en desacuerdo',4),(37,11,'Muy de acuerdo',1),(38,11,'De acuerdo',2),(39,11,'En desacuerdo',3),(40,11,'Muy en desacuerdo',4),(61,19,'Muy de acuerdo',1),(62,19,'De acuerdo',2),(63,19,'En desacuerdo',3),(64,19,'Muy en desacuerdo',4),(65,20,'Muy de acuerdo',1),(66,20,'De acuerdo',2),(67,20,'En desacuerdo',3),(68,20,'Muy en desacuerdo',4),(69,21,'Muy de acuerdo',1),(70,21,'De acuerdo',2),(71,21,'En desacuerdo',3),(72,21,'Muy en desacuerdo',4),(73,22,'Muy de acuerdo',1),(74,22,'De acuerdo',2),(75,22,'En desacuerdo',3),(76,22,'Muy en desacuerdo',4),(77,23,'Muy de acuerdo',1),(78,23,'De acuerdo',2),(79,23,'En desacuerdo',3),(80,23,'Muy en desacuerdo',4),(121,37,'Muy de acuerdo',1),(122,37,'De acuerdo',2),(123,37,'En desacuerdo',3),(124,37,'Muy en desacuerdo',4),(125,38,'Muy de acuerdo',1),(126,38,'De acuerdo',2),(127,38,'En desacuerdo',3),(128,38,'Muy en desacuerdo',4),(129,39,'Muy de acuerdo',1),(130,39,'De acuerdo',2),(131,39,'En desacuerdo',3),(132,39,'Muy en desacuerdo',4),(133,40,'Muy de acuerdo',1),(134,40,'De acuerdo',2),(135,40,'En desacuerdo',3),(136,40,'Muy en desacuerdo',4),(137,41,'Muy de acuerdo',1),(138,41,'De acuerdo',2),(139,41,'En desacuerdo',3),(140,41,'Muy en desacuerdo',4),(141,43,'Muy de acuerdo',1),(142,43,'De acuerdo',2),(143,43,'En desacuerdo',3),(144,43,'Muy en desacuerdo',4),(145,44,'Muy de acuerdo',1),(146,44,'De acuerdo',2),(147,44,'En desacuerdo',3),(148,44,'Muy en desacuerdo',4),(149,45,'Muy de acuerdo',1),(150,45,'De acuerdo',2),(151,45,'En desacuerdo',3),(152,45,'Muy en desacuerdo',4),(153,46,'Muy de acuerdo',1),(154,46,'De acuerdo',2),(155,46,'En desacuerdo',3),(156,46,'Muy en desacuerdo',4),(157,47,'Muy de acuerdo',1),(158,47,'De acuerdo',2),(159,47,'En desacuerdo',3),(160,47,'Muy en desacuerdo',4),(161,49,'Muy de acuerdo',1),(162,49,'De acuerdo',2),(163,49,'En desacuerdo',3),(164,49,'Muy en desacuerdo',4),(165,50,'Muy de acuerdo',1),(166,50,'De acuerdo',2),(167,50,'En desacuerdo',3),(168,50,'Muy en desacuerdo',4),(169,51,'Muy de acuerdo',1),(170,51,'De acuerdo',2),(171,51,'En desacuerdo',3),(172,51,'Muy en desacuerdo',4),(173,52,'Muy de acuerdo',1),(174,52,'De acuerdo',2),(175,52,'En desacuerdo',3),(176,52,'Muy en desacuerdo',4),(177,53,'Muy de acuerdo',1),(178,53,'De acuerdo',2),(179,53,'En desacuerdo',3),(180,53,'Muy en desacuerdo',4),(361,109,'Muy de acuerdo',1),(362,109,'De acuerdo',2),(363,109,'En desacuerdo',3),(364,109,'Muy en desacuerdo',4),(365,110,'Muy de acuerdo',1),(366,110,'De acuerdo',2),(367,110,'En desacuerdo',3),(368,110,'Muy en desacuerdo',4),(369,111,'Muy de acuerdo',1),(370,111,'De acuerdo',2),(371,111,'En desacuerdo',3),(372,111,'Muy en desacuerdo',4),(373,112,'Muy de acuerdo',1),(374,112,'De acuerdo',2),(375,112,'En desacuerdo',3),(376,112,'Muy en desacuerdo',4),(377,113,'Muy de acuerdo',1),(378,113,'De acuerdo',2),(379,113,'En desacuerdo',3),(380,113,'Muy en desacuerdo',4),(461,139,'Muy de acuerdo',1),(462,139,'De acuerdo',2),(463,139,'En desacuerdo',3),(464,139,'Muy en desacuerdo',4),(465,140,'Muy de acuerdo',1),(466,140,'De acuerdo',2),(467,140,'En desacuerdo',3),(468,140,'Muy en desacuerdo',4),(469,141,'Muy de acuerdo',1),(470,141,'De acuerdo',2),(471,141,'En desacuerdo',3),(472,141,'Muy en desacuerdo',4),(473,142,'Muy de acuerdo',1),(474,142,'De acuerdo',2),(475,142,'En desacuerdo',3),(476,142,'Muy en desacuerdo',4),(477,143,'Muy de acuerdo',1),(478,143,'De acuerdo',2),(479,143,'En desacuerdo',3),(480,143,'Muy en desacuerdo',4);
/*!40000 ALTER TABLE `choice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `docente_materia`
--

DROP TABLE IF EXISTS `docente_materia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `docente_materia` (
  `id_docente` int(11) NOT NULL,
  `id_materia` int(11) NOT NULL,
  PRIMARY KEY (`id_docente`,`id_materia`),
  KEY `docente_materia_ibfk_2` (`id_materia`),
  CONSTRAINT `docente_materia_ibfk_1` FOREIGN KEY (`id_docente`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `docente_materia_ibfk_2` FOREIGN KEY (`id_materia`) REFERENCES `materia` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `docente_materia`
--

LOCK TABLES `docente_materia` WRITE;
/*!40000 ALTER TABLE `docente_materia` DISABLE KEYS */;
INSERT INTO `docente_materia` VALUES (6,1),(6,2),(7,4),(8,15);
/*!40000 ALTER TABLE `docente_materia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `form`
--

DROP TABLE IF EXISTS `form`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `form` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `id_docente` int(11) DEFAULT NULL,
  `id_materia` int(11) DEFAULT NULL,
  `start_at` datetime DEFAULT NULL,
  `end_at` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `fk_form_materia` (`id_materia`),
  KEY `form_ibfk_1` (`id_docente`),
  CONSTRAINT `fk_form_materia` FOREIGN KEY (`id_materia`) REFERENCES `materia` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `form_ibfk_1` FOREIGN KEY (`id_docente`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form`
--

LOCK TABLES `form` WRITE;
/*!40000 ALTER TABLE `form` DISABLE KEYS */;
INSERT INTO `form` VALUES (1,'Materia: Cómputo Cuántico','Evaluación general de la materia',NULL,1,'2025-10-01 00:00:00','2025-12-31 23:59:59',1),(2,'Materia: Ciberseguridad','Evaluación general de la materia',NULL,2,'2025-10-01 00:00:00','2025-12-31 23:59:59',1),(4,'Materia: Criptografía','Evaluación general de la materia',NULL,4,'2025-10-01 00:00:00','2025-12-31 23:59:59',1),(7,'Paulina Bautista','Evaluación del/la docente (Paulina Bautista)',6,NULL,'2025-10-01 00:00:00','2025-12-31 23:59:59',1),(8,'Docente: Montserrat Mariscal','Evaluación del/la docente (Montserrat Mariscal)',7,NULL,'2025-10-01 00:00:00','2025-12-31 23:59:59',1),(9,'Docente: José Ramírez','Evaluación del/la docente (José Ramírez)',8,NULL,'2025-10-01 00:00:00','2025-12-31 23:59:59',1),(19,'Form - Materia: nlp','Evaluación de la materia (nlp)',NULL,13,'2025-11-27 02:56:21','2025-12-31 23:59:59',1),(24,'Form - Materia: lecheria','Evaluación de la materia (lecheria)',NULL,15,'2025-11-27 03:25:10','2025-12-31 23:59:59',1);
/*!40000 ALTER TABLE `form` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grupo`
--

DROP TABLE IF EXISTS `grupo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `grupo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `descripcion` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grupo`
--

LOCK TABLES `grupo` WRITE;
/*!40000 ALTER TABLE `grupo` DISABLE KEYS */;
INSERT INTO `grupo` VALUES (1,'LIA01',NULL),(2,'LFM01',NULL),(3,'LFC01',NULL);
/*!40000 ALTER TABLE `grupo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `materia`
--

DROP TABLE IF EXISTS `materia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `materia` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `materia`
--

LOCK TABLES `materia` WRITE;
/*!40000 ALTER TABLE `materia` DISABLE KEYS */;
INSERT INTO `materia` VALUES (1,'Cómputo Cuántico'),(2,'Ciberseguridad'),(4,'Criptografía'),(13,'nlp'),(15,'lecheria');
/*!40000 ALTER TABLE `materia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `materia_grupo`
--

DROP TABLE IF EXISTS `materia_grupo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `materia_grupo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_materia` int(11) NOT NULL,
  `id_grupo` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `materia_grupo_ibfk_1` (`id_materia`),
  KEY `materia_grupo_ibfk_2` (`id_grupo`),
  CONSTRAINT `materia_grupo_ibfk_1` FOREIGN KEY (`id_materia`) REFERENCES `materia` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `materia_grupo_ibfk_2` FOREIGN KEY (`id_grupo`) REFERENCES `grupo` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `materia_grupo`
--

LOCK TABLES `materia_grupo` WRITE;
/*!40000 ALTER TABLE `materia_grupo` DISABLE KEYS */;
INSERT INTO `materia_grupo` VALUES (1,1,1),(2,2,1),(4,4,2),(20,13,2),(23,15,1);
/*!40000 ALTER TABLE `materia_grupo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `question`
--

DROP TABLE IF EXISTS `question`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `question` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_form` int(11) DEFAULT NULL,
  `texto_pregunta` varchar(255) DEFAULT NULL,
  `tipo` enum('multiple','texto') DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `question_ibfk_1` (`id_form`),
  CONSTRAINT `question_ibfk_1` FOREIGN KEY (`id_form`) REFERENCES `form` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=151 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `question`
--

LOCK TABLES `question` WRITE;
/*!40000 ALTER TABLE `question` DISABLE KEYS */;
INSERT INTO `question` VALUES (1,1,'El profesor explica los conceptos claramente.','multiple'),(2,1,'El profesor fomenta la participación.','multiple'),(3,1,'El material y prácticas están relacionados con la materia.','multiple'),(4,1,'La evaluación refleja lo visto en clase.','multiple'),(5,1,'El profesor muestra interés por el aprendizaje del alumnado.','multiple'),(6,1,'Comentarios adicionales (texto libre).','texto'),(7,2,'El profesor explica los conceptos claramente.','multiple'),(8,2,'El profesor fomenta la participación.','multiple'),(9,2,'El material y prácticas están relacionados con la materia.','multiple'),(10,2,'La evaluación refleja lo visto en clase.','multiple'),(11,2,'El profesor muestra interés por el aprendizaje del alumnado.','multiple'),(12,2,'Comentarios adicionales (texto libre).','texto'),(19,4,'El profesor explica los conceptos claramente.','multiple'),(20,4,'El profesor fomenta la participación.','multiple'),(21,4,'El material y prácticas están relacionados con la materia.','multiple'),(22,4,'La evaluación refleja lo visto en clase.','multiple'),(23,4,'El profesor muestra interés por el aprendizaje del alumnado.','multiple'),(24,4,'Comentarios adicionales (texto libre).','texto'),(37,7,'El docente explica los conceptos claramente.','multiple'),(38,7,'El docente fomenta la participación.','multiple'),(39,7,'El docente domina el contenido.','multiple'),(40,7,'Los recursos son adecuados.','multiple'),(41,7,'El docente muestra interés por el aprendizaje.','multiple'),(42,7,'Comentarios adicionales (texto libre).','texto'),(43,8,'El docente explica los conceptos claramente.','multiple'),(44,8,'El docente fomenta la participación.','multiple'),(45,8,'El docente domina el contenido.','multiple'),(46,8,'Los recursos son adecuados.','multiple'),(47,8,'El docente muestra interés por el aprendizaje.','multiple'),(48,8,'Comentarios adicionales (texto libre).','texto'),(49,9,'El docente explica los conceptos claramente.','multiple'),(50,9,'El docente fomenta la participación.','multiple'),(51,9,'El docente domina el contenido.','multiple'),(52,9,'Los recursos son adecuados.','multiple'),(53,9,'El docente muestra interés por el aprendizaje.','multiple'),(54,9,'Comentarios adicionales (texto libre).','texto'),(109,19,'Los temas son interesantes','multiple'),(110,19,'El semestre es suficiente para abarcar lo necesario','multiple'),(111,19,'El temario es completo.','multiple'),(112,19,'Los recursos son adecuados.','multiple'),(113,19,'Me interesa el contenido de la materia.','multiple'),(114,19,'Comentarios adicionales (texto libre).','texto'),(139,24,'Los temas son interesantes','multiple'),(140,24,'El semestre es suficiente para abarcar lo necesario','multiple'),(141,24,'El temario es completo.','multiple'),(142,24,'Los recursos son adecuados.','multiple'),(143,24,'Me interesa el contenido de la materia.','multiple'),(144,24,'Comentarios adicionales (texto libre).','texto');
/*!40000 ALTER TABLE `question` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `response`
--

DROP TABLE IF EXISTS `response`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `response` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_form` int(11) NOT NULL,
  `id_alumnx` int(11) NOT NULL,
  `submitted_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_form` (`id_form`,`id_alumnx`),
  UNIQUE KEY `unique_form_user` (`id_form`,`id_alumnx`),
  KEY `response_ibfk_2` (`id_alumnx`),
  CONSTRAINT `response_ibfk_1` FOREIGN KEY (`id_form`) REFERENCES `form` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `response_ibfk_2` FOREIGN KEY (`id_alumnx`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `response`
--

LOCK TABLES `response` WRITE;
/*!40000 ALTER TABLE `response` DISABLE KEYS */;
INSERT INTO `response` VALUES (15,8,2,'2025-10-25 20:34:24'),(16,8,4,'2025-11-03 21:55:40'),(28,9,5,'2025-11-13 10:10:27'),(29,8,5,'2025-11-13 11:10:49'),(31,7,2,'2025-11-27 02:42:06'),(35,24,4,'2025-11-28 19:29:14'),(36,7,4,'2025-11-28 19:58:03');
/*!40000 ALTER TABLE `response` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `matricula` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` enum('alumnx','docente','admin') DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `current_session_token` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`matricula`),
  UNIQUE KEY `matricula` (`matricula`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Admin General','00000','2637a5c30af69a7bad877fdb65fbd78b','admin','2025-10-24 04:26:59','2025-11-29 03:50:18',NULL),(2,'Annie Bonnav','A001','31e83f15874c1ee3eacf27126f309101','alumnx','2025-10-24 04:26:59','2025-11-27 09:16:52',NULL),(4,'Diego Valeriano','A003','ae2b1fca515949e5d54fb22b8ed95575','alumnx','2025-10-24 04:26:59','2025-11-29 01:58:07',NULL),(5,'Mariana López','A004','763e17002434522aa69770493b56dad3','alumnx','2025-10-24 04:26:59','2025-11-29 04:11:47',NULL),(6,'Paulina Bautista','D001','a4ff69a00255b0d44e8be6f629f6ca2c','docente','2025-10-24 04:26:59','2025-11-29 04:11:54','8652a99a3d394a8a8d1fa4a84f23e8d5'),(7,'Montserrat Mariscal','D002','6a360805c2e9a84fcbfa81ea744eac53','docente','2025-10-24 04:26:59','2025-11-29 03:57:47',NULL),(8,'José Ramírez','D003','8c2cb7fe37e7bdc078a1f4cf6b8d8794','docente','2025-10-24 04:26:59',NULL,NULL),(34,'Prueba Docente','234346','50f84daf3a6dfd6a9f20c9f8ef428942','docente','2025-11-19 20:47:13',NULL,NULL),(37,'Student example','q34346','f52854cc99ae1c1966b0a21d0127975b','alumnx','2025-11-19 20:51:05',NULL,NULL),(40,'Docente example','0921378','7815696ecbf1c96e6894b779456d330e','docente','2025-11-19 21:00:33','2025-11-19 21:48:02',NULL),(42,'Testeo alumnx','097855','fb4d0c4bc7fa4752016620069bf0970c','alumnx','2025-11-20 15:55:03',NULL,NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'evaluaciones'
--

--
-- Dumping routines for database 'evaluaciones'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-29 21:56:00
